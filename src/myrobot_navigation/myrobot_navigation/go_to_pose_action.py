#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from enum import Enum
import math
import time

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped, Quaternion
from myrobot_actions.action import NavigateToPose

class NavigationState(Enum):
    ALIGN_TO_GOAL = 0
    MOVE_TO_GOAL = 1
    ALIGN_TO_FINAL = 2

class GoToPoseActionServer(Node):
    def __init__(self):
        super().__init__('go_to_pose_action_server')

        self.callback_group_ = ReentrantCallbackGroup()

        # Subscribers and Publishers
        self.odom_subscriber_ = self.create_subscription(
            Odometry,
            '/odometry/filtered',
            self.odom_callback,
            10,
            callback_group=self.callback_group_
        )
        self.cmd_vel_publisher_ = self.create_publisher(
            TwistStamped,
            '/myrobot_controller/cmd_vel',
            10
        )

        # Action Server setup
        self.action_server_ = ActionServer(
            self,
            NavigateToPose,
            'navigate_to_pose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group_
        )

        # Robot State variables
        self.current_x_ = 0.0
        self.current_y_ = 0.0
        self.current_yaw_ = 0.0

        # Control Parameters (can be adjusted via ROS parameters)
        self.declare_parameter('k_v', 0.9)
        self.declare_parameter('k_w', 1.7)
        self.k_v_ = self.get_parameter('k_v').value
        self.k_w_ = self.get_parameter('k_w').value

        # Tolerances & Saturation limits
        self.declare_parameter('dist_tolerance', 0.01)     # 1 cm
        self.declare_parameter('align_tolerance', 0.01)    # ~0.5 degrees
        self.declare_parameter('final_tolerance', 0.01)    # ~0.5 degrees
        self.declare_parameter('v_max', 2.0)               # max linear speed (m/s)
        self.declare_parameter('w_max', 3.5)               # max angular speed (rad/s)

        self.dist_tolerance_ = self.get_parameter('dist_tolerance').value
        self.align_tolerance_ = self.get_parameter('align_tolerance').value
        self.final_tolerance_ = self.get_parameter('final_tolerance').value
        self.v_max_ = self.get_parameter('v_max').value
        self.w_max_ = self.get_parameter('w_max').value

        self.get_logger().info("Go-To-Pose Action Server successfully initialized!")

    def odom_callback(self, msg: Odometry) -> None:
        # Extract orientation quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw_ = math.atan2(siny_cosp, cosy_cosp)
        self.current_x_ = msg.pose.pose.position.x
        self.current_y_ = msg.pose.pose.position.y
        #self.get_logger().info(f"Odometry update - Position: ({self.current_x_:.2f}, {self.current_y_:.2f}), Yaw: {math.degrees(self.current_yaw_):.1f}°")

    def goal_callback(self, goal_request):
        self.get_logger().info('Received a new navigation goal request.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request for the active navigation goal.')
        return CancelResponse.ACCEPT

    def get_yaw_from_quaternion(self, q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny_cosp, cosy_cosp)

    def yaw_to_quaternion(self, yaw):
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw / 2.0)
        q.w = math.cos(yaw / 2.0)
        return q

    def warp_angle(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def stop_robot(self):
        self.publish_velocity(0.0, 0.0)

    def publish_velocity(self, linear, angular):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = linear
        msg.twist.angular.z = angular
        self.cmd_vel_publisher_.publish(msg)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing NavigateToPose goal...')
        start_time = time.time()

        # Extract target goal pose
        target_pose = goal_handle.request.pose
        target_x = target_pose.pose.position.x
        target_y = target_pose.pose.position.y
        target_yaw = self.get_yaw_from_quaternion(target_pose.pose.orientation)

        # Set initial FSM state
        state = NavigationState.ALIGN_TO_GOAL
        rate = self.create_rate(20)  # 20 Hz loop rate for smooth control

        feedback_msg = NavigateToPose.Feedback()
        result = NavigateToPose.Result()

        while rclpy.ok():
            # Check for cancellation requests
            if goal_handle.is_cancel_requested:
                self.stop_robot()
                goal_handle.canceled()
                self.get_logger().info('Goal execution cancelled successfully.')
                result.success = False
                result.final_distance = math.sqrt((target_x - self.current_x_)**2 + (target_y - self.current_y_)**2)
                result.final_angle_error = self.warp_angle(target_yaw - self.current_yaw_)
                return result

            # 1. Error calculations
            dx = target_x - self.current_x_
            dy = target_y - self.current_y_
            distance_to_goal = math.sqrt(dx**2 + dy**2)

            # Target heading angle relative to current orientation
            bearing_to_goal = math.atan2(dy, dx)
            heading_error = self.warp_angle(bearing_to_goal - self.current_yaw_)
            final_yaw_error = self.warp_angle(target_yaw - self.current_yaw_)

            # Initialize control velocities
            linear_v = 0.0
            angular_w = 0.0

            # 2. State Machine Logic
            if state == NavigationState.ALIGN_TO_GOAL:
                # Rotate in place towards target point
                angular_w = self.k_w_ * heading_error
                # Cap angular velocity
                angular_w = max(-self.w_max_, min(self.w_max_, angular_w))
                
                self.get_logger().info(
                    f"[ALIGN] Distance: {distance_to_goal:.2f}m, Heading Err: {math.degrees(heading_error):.1f}°",
                    throttle_duration_sec=1.0
                )

                if abs(heading_error) < self.align_tolerance_:
                    state = NavigationState.MOVE_TO_GOAL
                    self.get_logger().info("Aligned with target. Moving to goal position.")

            elif state == NavigationState.MOVE_TO_GOAL:
                # Drive forward to target coordinates, correcting heading dynamically
                linear_v = self.k_v_ * distance_to_goal
                angular_w = self.k_w_ * heading_error

                # Apply saturation limits
                linear_v = max(0.0, min(self.v_max_, linear_v))
                angular_w = max(-self.w_max_, min(self.w_max_, angular_w))

                self.get_logger().info(
                    f"[MOVE] Distance: {distance_to_goal:.2f}m, Heading Err: {math.degrees(heading_error):.1f}°",
                    throttle_duration_sec=1.0
                )

                # If we get way off course, realign in place
                if abs(heading_error) > 0.5:
                    state = NavigationState.ALIGN_TO_GOAL
                    self.get_logger().info("Heading error too large. Re-aligning to goal.")

                # Check if arrived at target coordinates
                if distance_to_goal < self.dist_tolerance_:
                    state = NavigationState.ALIGN_TO_FINAL
                    self.get_logger().info("Goal coordinates reached. Orienting to final heading.")

            elif state == NavigationState.ALIGN_TO_FINAL:
                # Rotate in place to align with the final target orientation
                angular_w = self.k_w_ * final_yaw_error
                angular_w = max(-self.w_max_, min(self.w_max_, angular_w))

                self.get_logger().info(
                    f"[ORIENT] Final Yaw Err: {math.degrees(final_yaw_error):.1f}°",
                    throttle_duration_sec=1.0
                )

                # Check if final orientation is achieved
                if abs(final_yaw_error) < self.final_tolerance_:
                    break

            # Publish calculated velocities
            self.publish_velocity(linear_v, angular_w)

            # Publish action feedback
            feedback_msg.current_pose.header.stamp = self.get_clock().now().to_msg()
            feedback_msg.current_pose.header.frame_id = 'odom'
            feedback_msg.current_pose.pose.position.x = self.current_x_
            feedback_msg.current_pose.pose.position.y = self.current_y_
            feedback_msg.current_pose.pose.orientation = self.yaw_to_quaternion(self.current_yaw_)
            feedback_msg.distance_remaining = distance_to_goal
            feedback_msg.angle_remaining = abs(final_yaw_error) if state == NavigationState.ALIGN_TO_FINAL else abs(heading_error)
            feedback_msg.elapsed_time = time.time() - start_time
            goal_handle.publish_feedback(feedback_msg)

            rate.sleep()

        # Complete and stop
        self.stop_robot()
        goal_handle.succeed()
        self.get_logger().info("Target pose successfully reached!")

        # Populate final results
        result.success = True
        result.final_distance = distance_to_goal
        result.final_angle_error = final_yaw_error
        return result

def main(args=None):
    rclpy.init(args=args)
    node = GoToPoseActionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()