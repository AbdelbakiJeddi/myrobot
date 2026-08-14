#!/usr/bin/env python3
"""
Simple Navigator — Stage 3: single waypoint ALIGN + DRIVE.

States:
  NEED_POSE → wait until /odometry/filtered has produced a pose
  ALIGN     → rotate to face the bearing of (wp_x, wp_y)
  DRIVE     → drive toward the point with trapezoid profiler + heading PID
  ORIENT    → (optional) spin to final yaw wp_yaw once arrived
  DONE      → stopped, mission complete

Pose from /odometry/filtered (EKF), cmd_vel to /myrobot_controller/cmd_vel.

ALIGN/ORIENT use `steer_pid()` (PID on heading, damped from odom yaw rate,
anti-windup integral, ramped min velocity near tolerance for stall). Settled
requires small error AND small rate.

DRIVE: bearing re-computed each tick toward the point; v comes from the
symmetric trapezoid profiler (accel ~ travelled, decel ~ to_go, cruise at
v_max), heading held by the PID. If heading error exceeds `realign_threshold`
the FSM re-enters ALIGN. Settled: to_go < pos_tol AND |lin_vel| < lin_thresh,
then optional ORIENT, else DONE.

Watchdogs: odom staleness and per-state timeout abort the mission (stop first).
"""
import math
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class _IntegralState:
    def __init__(self):
        self.value = 0.0

    def reset(self):
        self.value = 0.0


class _State(Enum):
    NEED_POSE = auto()
    ALIGN = auto()
    DRIVE = auto()
    ORIENT = auto()
    DONE = auto()


class Navigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')

        # ── waypoint params ──────────────────────────────────────────────
        self.declare_parameter("wp_x", 0.0)             # target point, arena frame [m]
        self.declare_parameter("wp_y", 0.0)
        self.declare_parameter("wp_yaw", 0.0)           # final heading [rad] after arrival

        # ── rotate params ────────────────────────────────────────────────
        self.declare_parameter("kp_rotate", 1.5)
        self.declare_parameter("ki_rotate", 0.2)        # kills gyro-bias drift
        self.declare_parameter("kd_rotate", 0.4)        # damps from yaw_rate
        self.declare_parameter("w_max", 3.0)
        self.declare_parameter("min_w_rotate", 0.15)    # ramp floor near tol
        self.declare_parameter("min_overshoot_rate", 0.08)  # floor only when stalled
        self.declare_parameter("align_tol", 0.02)       # rad
        self.declare_parameter("ang_vel_thresh", 0.05)  # rad/s, "settled"

        # ── drive params ─────────────────────────────────────────────────
        self.declare_parameter("v_max", 0.3)            # cruise speed [m/s]
        self.declare_parameter("a_max", 0.2)            # accel/decel [m/s²]
        self.declare_parameter("pos_tol", 0.02)         # m, "arrived"
        self.declare_parameter("lin_thresh", 0.03)      # m/s, "settled"
        self.declare_parameter("kp_drive", 1.5)
        self.declare_parameter("ki_drive", 0.1)
        self.declare_parameter("kd_drive", 0.4)
        self.declare_parameter("integral_max", 0.5)     # rad·s clamp (windup)
        self.declare_parameter("realign_threshold", 0.35)  # rad, re-ALIGN while driving

        # ── safety params ────────────────────────────────────────────────
        self.declare_parameter("odom_timeout", 0.5)     # s
        self.declare_parameter("max_state_time", 10.0)  # s, stuck protection
        self.declare_parameter("rate_hz", 20.0)

        self.wp_x_ = float(self.get_parameter("wp_x").value)
        self.wp_y_ = float(self.get_parameter("wp_y").value)
        self.wp_yaw_ = float(self.get_parameter("wp_yaw").value)

        self.kp_rot_ = float(self.get_parameter("kp_rotate").value)
        self.ki_rot_ = float(self.get_parameter("ki_rotate").value)
        self.kd_rot_ = float(self.get_parameter("kd_rotate").value)
        self.w_max_ = float(self.get_parameter("w_max").value)
        self.min_w_ = float(self.get_parameter("min_w_rotate").value)
        self.min_ovr_ = float(self.get_parameter("min_overshoot_rate").value)
        self.align_tol_ = float(self.get_parameter("align_tol").value)
        self.ang_thresh_ = float(self.get_parameter("ang_vel_thresh").value)

        self.v_max_ = float(self.get_parameter("v_max").value)
        self.a_max_ = float(self.get_parameter("a_max").value)
        self.pos_tol_ = float(self.get_parameter("pos_tol").value)
        self.lin_thresh_ = float(self.get_parameter("lin_thresh").value)
        self.kp_drv_ = float(self.get_parameter("kp_drive").value)
        self.ki_drv_ = float(self.get_parameter("ki_drive").value)
        self.kd_drv_ = float(self.get_parameter("kd_drive").value)
        self.int_max_ = float(self.get_parameter("integral_max").value)
        self.realign_thr_ = float(self.get_parameter("realign_threshold").value)

        self.odom_timeout_ = float(self.get_parameter("odom_timeout").value)
        self.max_state_time_ = float(self.get_parameter("max_state_time").value)
        self.rate_hz_ = float(self.get_parameter("rate_hz").value)
        self.dt_ = 1.0 / self.rate_hz_

        # precomputed constants (avoid per-tick recompute)
        self._two_a_ = 2.0 * self.a_max_
        self._int_gate_ = self.align_tol_ * 25.0   # ~0.5 rad, integral kill-band

        self._odom_sub = self.create_subscription(
            Odometry, "/odometry/filtered", self._odom_cb, qos_profile_sensor_data)
        self._cmd_pub = self.create_publisher(
            TwistStamped, "/myrobot_controller/cmd_vel", 10)

        # odometry snapshot (single-threaded executor serialises callbacks)
        self._pose_ready = False
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.yaw_rate = 0.0
        self.lin_vel = 0.0
        self._last_odom_time = self.get_clock().now()

        # drive bookkeeping
        self._start_x = 0.0
        self._start_y = 0.0

        # integral accumulators (per control phase, reset on entry)
        self._rot_state = _IntegralState()
        self._drv_state = _IntegralState()

        # FSM
        # FSM
        self._state = _State.NEED_POSE
        self._state_entry = self.get_clock().now()

        self._timer = self.create_timer(self.dt_, self._control_cb)

        self.get_logger().info(
            f'Simple Navigator ready. waypoint=({self.wp_x_:.2f}, {self.wp_y_:.2f}) '
            f'yaw={math.degrees(self.wp_yaw_):.1f}°.')

    # ── ROS callbacks ───────────────────────────────────────────────────
    def _odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.yaw = self._yaw_from_quaternion(msg.pose.pose.orientation)
        self.yaw_rate = msg.twist.twist.angular.z
        self.lin_vel = msg.twist.twist.linear.x
        self._last_odom_time = self.get_clock().now()
        self._pose_ready = True

    def _control_cb(self):
        if self._state is _State.DONE:
            return

        now = self.get_clock().now()

        # NEED_POSE: server only gate — wait for first pose, no watchdog yet.
        if self._state is _State.NEED_POSE:
            if not self._pose_ready:
                self.get_logger().info("Waiting for odometry...", throttle_duration_sec=2.0)
                return
            self._enter_align(now)
            return

        # From here on a pose has been seen: watchdogs are honest.
        odom_age = (now - self._last_odom_time).nanoseconds / 1e9
        if odom_age > self.odom_timeout_:
            self.get_logger().error(
                f"Odometry stale ({odom_age:.2f}s > {self.odom_timeout_}s). Aborting.")
            self._stop()
            self._state = _State.DONE
            return

        if (now - self._state_entry).nanoseconds / 1e9 > self.max_state_time_:
            self.get_logger().error(
                f"State {self._state.name} timed out after {self.max_state_time_}s. Aborting.")
            self._stop()
            self._state = _State.DONE
            return

        if self._state is _State.ALIGN:
            self._align()
        elif self._state is _State.DRIVE:
            self._drive()
        elif self._state is _State.ORIENT:
            self._orient()

    # ── state transitions ───────────────────────────────────────────────
    def _enter_align(self, now):
        self._state = _State.ALIGN
        self._state_entry = now
        self._rot_state.reset()
        self.get_logger().info(
            f"→ ALIGN to ({self.wp_x_:.2f}, {self.wp_y_:.2f}) "
            f"bearing={math.degrees(self._bearing()):.1f}°.")

    def _enter_drive(self, now):
        self._state = _State.DRIVE
        self._state_entry = now
        self._start_x, self._start_y = self.x, self.y
        self._drv_state.reset()
        self.get_logger().info(
            f"→ DRIVE, to_go={self._to_go():.2f} m.")

    def _enter_orient(self, now):
        self._state = _State.ORIENT
        self._state_entry = now
        self._rot_state.reset()
        self.get_logger().info(f"→ ORIENT to {math.degrees(self.wp_yaw_):.1f}°.")

    # ── geometry helpers ────────────────────────────────────────────────
    def _bearing(self) -> float:
        return math.atan2(self.wp_y_ - self.y, self.wp_x_ - self.x)

    def _to_go(self) -> float:
        return math.hypot(self.wp_x_ - self.x, self.wp_y_ - self.y)

    # ── ALIGN ───────────────────────────────────────────────────────────
    def _align(self):
        err = self.normalize(self._bearing() - self.yaw)
        w = self.steer_pid(err, self.yaw_rate, (self.kp_rot_, self.ki_rot_, self.kd_rot_),
                           self._rot_state, use_floor=True)

        settled = abs(err) < self.align_tol_ and abs(self.yaw_rate) < self.ang_thresh_
        if settled:
            self.get_logger().info(
                f"Align settled: err={math.degrees(err):.2f}°, "
                f"yaw_rate={self.yaw_rate:.3f} rad/s. "
                f"Yaw={math.degrees(self.yaw):.1f}°.")
            self._stop()
            self._enter_drive(self.get_clock().now())
            return

        self._publish_cmd(0.0, w)

    # ── DRIVE ───────────────────────────────────────────────────────────
    def _drive(self):
        dx = self.wp_x_ - self.x
        dy = self.wp_y_ - self.y
        to_go = math.hypot(dx, dy)
        bearing = math.atan2(dy, dx)

        heading_err = self.normalize(bearing - self.yaw)
        if abs(heading_err) > self.realign_thr_:
            self.get_logger().warn(
                f"Heading err {math.degrees(heading_err):.1f}° > "
                f"{math.degrees(self.realign_thr_):.1f}° — re-aligning.")
            self._stop()
            self._enter_align(self.get_clock().now())
            return

        w = self.steer_pid(heading_err, self.yaw_rate,
                           (self.kp_drv_, self.ki_drv_, self.kd_drv_),
                           self._drv_state, use_floor=False)

        # progress along the start→goal axis (>= 0), keeps the accel curve
        # honest even if the path arcs sideways
        tot_x = self.wp_x_ - self._start_x
        tot_y = self.wp_y_ - self._start_y
        leg = math.hypot(tot_x, tot_y)
        progress = self._clamp(
            ((self.x - self._start_x) * tot_x + (self.y - self._start_y) * tot_y) / max(leg, 1e-9),
            leg)
        progress = max(progress, 0.0)

        v = self._profile(to_go, progress)

        settled = to_go < self.pos_tol_ and abs(self.lin_vel) < self.lin_thresh_
        if settled:
            self.get_logger().info(
                f"Arrived: to_go={to_go:.3f} m, speed={self.lin_vel:.3f} m/s. "
                f"Progress={progress:.3f} m.")
            self._stop()
            self._enter_orient(self.get_clock().now())
            return

        self._publish_cmd(v, w)

    def _profile(self, to_go: float, travelled: float) -> float:
        """Symmetric trapezoid velocity profile.

        v = min(v_max, sqrt(2·a·travelled), sqrt(2·a·to_go))
        Accel curve ~ travelled (progress), decel curve ~ to_go. They meet at
        mid-leg → cruise at v_max. Short legs → triangle (no cruise).
        """
        a = self._two_a_
        v_accel = math.sqrt(a * max(travelled, 0.0))
        v_brake = math.sqrt(a * max(to_go, 0.0))
        return min(self.v_max_, v_accel, v_brake)

    # ── ORIENT ──────────────────────────────────────────────────────────
    def _orient(self):
        err = self.normalize(self.wp_yaw_ - self.yaw)
        w = self.steer_pid(err, self.yaw_rate, (self.kp_rot_, self.ki_rot_, self.kd_rot_),
                           self._rot_state, use_floor=True)

        settled = abs(err) < self.align_tol_ and abs(self.yaw_rate) < self.ang_thresh_
        if settled:
            self.get_logger().info(
                f"Orient settled: err={math.degrees(err):.2f}°, "
                f"final yaw={math.degrees(self.yaw):.1f}°.")
            self._stop()
            self._state = _State.DONE
            return

        self._publish_cmd(0.0, w)

    # ── shared steering PID ─────────────────────────────────────────────
    def steer_pid(self, err: float, yaw_rate: float, gains, istate: "_IntegralState",
                  use_floor: bool) -> float:
        """PID on heading error, damped from odom yaw rate.

        Anti-windup: integral only integrates near the setpoint and freezes
        while the command is saturated, then is clamped to `integral_max`.
        The minimum-velocity floor (anti-stall near tolerance) only engages
        when the robot is stalled, so it never overrides braking.
        """
        kp, ki, kd = gains

        w_unclamped = kp * err + ki * istate.value - kd * yaw_rate
        saturated = abs(w_unclamped) >= self.w_max_
        if not saturated and abs(err) <= self._int_gate_:
            istate.value += err * self.dt_
        istate.value = self._clamp(istate.value, self.int_max_)

        w = self._clamp(kp * err + ki * istate.value - kd * yaw_rate, self.w_max_)

        if use_floor and abs(err) > self.align_tol_ and abs(yaw_rate) < self.min_ovr_:
            min_w = self.min_w_ * min(abs(err) / (3.0 * self.align_tol_), 1.0)
            w = math.copysign(max(abs(w), min_w), w)

        # re-clamp after the floor so min_w can never exceed w_max
        return math.copysign(min(abs(w), self.w_max_), w)

    # ── helpers ─────────────────────────────────────────────────────────
    def _publish_cmd(self, v: float, w: float) -> None:
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_footprint"
        msg.twist.linear.x = float(v)
        msg.twist.angular.z = float(w)
        self._cmd_pub.publish(msg)

    def _stop(self) -> None:
        self._publish_cmd(0.0, 0.0)

    @staticmethod
    def _yaw_from_quaternion(q) -> float:
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny, cosy)

    @staticmethod
    def _clamp(value: float, limit: float) -> float:
        return max(-limit, min(limit, value))

    @staticmethod
    def normalize(angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return math.atan2(math.sin(angle), math.cos(angle))


def main():
    rclpy.init()
    node = Navigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()