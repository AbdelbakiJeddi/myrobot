#!/usr/bin/env python3
"""
GoToGoal Action Server — async FSM controller.

States:
  ALIGN  → rotate in place to face the goal position
  DRIVE  → drive forward toward goal, correcting heading
  ORIENT → rotate in place to match the final desired heading

Subscribes: /odometry/filtered  (nav_msgs/Odometry)
Publishes:  /myrobot_controller/cmd_vel  (geometry_msgs/TwistStamped)
Action:     navigate_to_pose  (myrobot_actions/NavigateToPose)
"""

import math
import threading
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import Quaternion, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from myrobot_actions.action import NavigateToPose


class _State(Enum):
    ALIGN = auto()
    DRIVE = auto()
    ORIENT = auto()


class GoToGoalServer(Node):
    """Non-blocking, async GoToGoal action server."""

    def __init__(self) -> None:
        super().__init__("go_to_goal_server")

        # -- parameters --
        self.declare_parameter("control_rate", 20.0)
        # Rotation states (ALIGN & ORIENT): heading correction
        self.declare_parameter("kp_rotate", 1.5)
        self.declare_parameter("kd_rotate", 0.1)
        # DRIVE state: distance + heading correction
        self.declare_parameter("kp_dist", 0.8)
        self.declare_parameter("kp_heading", 1.5)
        # Common parameters
        self.declare_parameter("v_max", 0.5)
        self.declare_parameter("w_max", 2.0)
        self.declare_parameter("position_tolerance", 0.05)
        self.declare_parameter("align_tolerance", 0.05)
        self.declare_parameter("orient_tolerance", 0.05)
        self.declare_parameter("realign_threshold", 0.5)
        self.declare_parameter("odom_timeout", 0.5)  # seconds
        # Thresholds for considering robot stopped
        self.declare_parameter("lin_vel_thresh", 0.01)  # m/s
        self.declare_parameter("ang_vel_thresh", 0.01)  # rad/s

        self._rate_hz = self.get_parameter("control_rate").value
        self._kp_rotate = self.get_parameter("kp_rotate").value
        self._kd_rotate = self.get_parameter("kd_rotate").value
        self._kp_dist = self.get_parameter("kp_dist").value
        self._kp_heading = self.get_parameter("kp_heading").value
        self._v_max = self.get_parameter("v_max").value
        self._w_max = self.get_parameter("w_max").value
        self._pos_tol = self.get_parameter("position_tolerance").value
        self._align_tol = self.get_parameter("align_tolerance").value
        self._orient_tol = self.get_parameter("orient_tolerance").value
        self._realign_thr = self.get_parameter("realign_threshold").value
        self._odom_timeout = self.get_parameter("odom_timeout").value
        self._lin_vel_thresh = self.get_parameter("lin_vel_thresh").value
        self._ang_vel_thresh = self.get_parameter("ang_vel_thresh").value


        self._odom_lock = threading.Lock()
        self._x = 0.0
        self._y = 0.0
        self._yaw = 0.0
        self._yaw_rate = 0.0
        self._linear_speed = 0.0
        self._last_odom_time = self.get_clock().now()


        cb_group = ReentrantCallbackGroup()


        self._odom_sub = self.create_subscription(
            Odometry,
            "/odometry/filtered",
            self._odom_cb,
            qos_profile_sensor_data,
            callback_group=cb_group,
        )


        self._cmd_pub = self.create_publisher(
            TwistStamped,
            "/myrobot_controller/cmd_vel",
            10,
        )

        self._action_server = ActionServer(
            self,
            NavigateToPose,
            "navigate_to_pose",
            execute_callback=self._execute,
            goal_callback=self._handle_goal,
            cancel_callback=self._handle_cancel,
            callback_group=cb_group,
        )

        self.get_logger().info("GoToGoal action server ready.")


    def _odom_cb(self, msg: Odometry) -> None:
        """Store latest pose and yaw rate (thread-safe)."""
        with self._odom_lock:
            self._x = msg.pose.pose.position.x
            self._y = msg.pose.pose.position.y
            self._yaw = self._yaw_from_quaternion(msg.pose.pose.orientation)
            self._yaw_rate = msg.twist.twist.angular.z
            # Calculate linear speed magnitude
            linear = msg.twist.twist.linear
            self._linear_speed = math.sqrt(linear.x**2 + linear.y**2 + linear.z**2)
            self._last_odom_time = self.get_clock().now()
    
    def _handle_goal(self, goal_request) -> GoalResponse:
        self.get_logger().info(
            f"Goal received: x={goal_request.goal_pose.pose.position.x:.2f}, "
            f"y={goal_request.goal_pose.pose.position.y:.2f}"
        )
        return GoalResponse.ACCEPT

    def _handle_cancel(self, goal_handle) -> CancelResponse:
        self.get_logger().info("Cancel requested.")
        return CancelResponse.ACCEPT

    def _execute(self, goal_handle):
        self.get_logger().info("Executing goal...")

        # Target
        gp = goal_handle.request.goal_pose.pose
        tx, ty = gp.position.x, gp.position.y
        t_yaw = self._yaw_from_quaternion(gp.orientation)

        state = _State.ALIGN
        rate = self.create_rate(self._rate_hz)
        feedback = NavigateToPose.Feedback()
        result = NavigateToPose.Result()

        while rclpy.ok():
            # --- cancel check ---
            if goal_handle.is_cancel_requested:
                self._stop()
                goal_handle.canceled()
                self.get_logger().info("Goal cancelled.")
                result.success = False
                result.final_position_error = self._distance(tx, ty)
                result.final_heading_error = abs(self._normalize(t_yaw - self._yaw))
                return result

            # --- snapshot odometry (thread-safe) ---
            with self._odom_lock:
                cx, cy, cyaw = self._x, self._y, self._yaw
                cyaw_rate = self._yaw_rate
                clin_speed = self._linear_speed
                odom_age = (self.get_clock().now() - self._last_odom_time).nanoseconds / 1e9

            # --- odom staleness watchdog ---
            if odom_age > self._odom_timeout:
                self._stop()
                goal_handle.abort()
                self.get_logger().error(
                    f"Odometry stale ({odom_age:.2f}s > {self._odom_timeout}s). Aborting goal."
                )
                result.success = False
                result.final_position_error = self._distance(tx, ty)
                result.final_heading_error = abs(self._normalize(t_yaw - cyaw))
                return result

            # --- errors ---
            dx = tx - cx
            dy = ty - cy
            dist = math.hypot(dx, dy)
            bearing = math.atan2(dy, dx)
            heading_err = self._normalize(bearing - cyaw)
            final_yaw_err = self._normalize(t_yaw - cyaw)

            # --- FSM ---
            if state is _State.ALIGN:
                v = 0.0
                w = self._compute_align(heading_err)
                if (
                    abs(heading_err) < self._align_tol
                    and abs(cyaw_rate) < self._ang_vel_thresh
                ):
                    state = _State.DRIVE
                    self.get_logger().info("ALIGN → DRIVE")

            elif state is _State.DRIVE:
                # Re-align if heading has drifted too far
                if abs(heading_err) > self._realign_thr:
                    state = _State.ALIGN
                    v = 0.0
                    w = self._compute_align(heading_err)
                    self.get_logger().info("DRIVE → ALIGN (re-align)")
                else:
                    v, w = self._compute_drive(dist, heading_err)
                    if dist < self._pos_tol and clin_speed < self._lin_vel_thresh:
                        state = _State.ORIENT
                        self.get_logger().info("DRIVE → ORIENT")

            elif state is _State.ORIENT:
                v = 0.0
                w = self._compute_orient(final_yaw_err)
                if (
                    abs(final_yaw_err) < self._orient_tol
                    and abs(cyaw_rate) < self._ang_vel_thresh
                ):
                    break

            self._publish_cmd(v, w)

            feedback.current_state = state.name
            feedback.distance_to_goal = dist
            goal_handle.publish_feedback(feedback)
            rate.sleep()

        self._stop()
        goal_handle.succeed()

        result.success = True
        result.final_position_error = self._distance(tx, ty)
        result.final_heading_error = abs(self._normalize(t_yaw - self._yaw))

        self.get_logger().info(
            f"Goal reached — pos_err={result.final_position_error:.3f} m, "
            f"head_err={math.degrees(result.final_heading_error):.1f}°"
        )
        return result


    def _compute_align(self, heading_err: float) -> float:
        """Return angular velocity for ALIGN state with PD control and ramped minimum velocity."""
        # PD control: proportional + derivative damping
        w = self._kp_rotate * heading_err - self._kd_rotate * self._yaw_rate
        w = self._clamp(w, self._w_max)

        # Ramp minimum velocity down as error approaches tolerance to prevent oscillation
        if abs(heading_err) > self._align_tol:
            min_w = 0.15 * min(abs(heading_err) / (3.0 * self._align_tol), 1.0)
            w = math.copysign(max(abs(w), min_w), w)

        return w

    def _compute_drive(self, distance: float, heading_err: float):
        """Return (linear_vel, angular_vel) for DRIVE state."""
        v = self._kp_dist * distance * math.cos(heading_err)
        v = min(max(v, 0.0), self._v_max)  # Clamp to [0, v_max]
        w = self._kp_heading * heading_err
        w = self._clamp(w, self._w_max)
        return v, w

    def _compute_orient(self, yaw_err: float) -> float:
        """Return angular velocity for ORIENT state with PD control and ramped minimum velocity."""
        # PD control: proportional + derivative damping
        w = self._kp_rotate * yaw_err - self._kd_rotate * self._yaw_rate
        w = self._clamp(w, self._w_max)

        # Ramp minimum velocity down as error approaches tolerance to prevent oscillation
        if abs(yaw_err) > self._orient_tol:
            min_w = 0.15 * min(abs(yaw_err) / (3.0 * self._orient_tol), 1.0)
            w = math.copysign(max(abs(w), min_w), w)

        return w


    def _publish_cmd(self, v: float, w: float) -> None:
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        msg.twist.linear.x = float(v)
        msg.twist.angular.z = float(w)
        self._cmd_pub.publish(msg)

    def _stop(self) -> None:
        self._publish_cmd(0.0, 0.0)

    @staticmethod
    def _normalize(angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return math.atan2(math.sin(angle), math.cos(angle))

    @staticmethod
    def _clamp(value: float, limit: float) -> float:
        return max(-limit, min(limit, value))

    @staticmethod
    def _yaw_from_quaternion(q) -> float:
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny, cosy)

    def _distance(self, tx: float, ty: float) -> float:
        return math.hypot(tx - self._x, ty - self._y)


def main(args=None):
    rclpy.init(args=args)
    node = GoToGoalServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
