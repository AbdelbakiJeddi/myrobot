#!/usr/bin/env python3
"""
GoToGoal Action Client — waypoint sequencer.

Loads named waypoints (goal_0, goal_1, …) from parameters and sends
them sequentially to the GoToGoal action server.
"""

import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped, Quaternion
from myrobot_actions.action import NavigateToPose


class GoToGoalClient(Node):
    """Sends a sequence of waypoints as action goals."""

    def __init__(self) -> None:
        super().__init__('go_to_goal_client')

        self.declare_parameter('yaw_in_degrees', True)
        self._yaw_deg = self.get_parameter('yaw_in_degrees').value

        self._waypoints = self._load_waypoints()
        if not self._waypoints:
            raise RuntimeError('No waypoints found. Set goal_0.x/y/yaw, goal_1.x/y/yaw, … parameters.')

        self.get_logger().info(f'Loaded {len(self._waypoints)} waypoint(s).')

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._index = 0

    # ------------------------------------------------------------------ #
    #  Waypoint loading
    # ------------------------------------------------------------------ #
    def _load_waypoints(self) -> list:
        """
        Iterate goal_0, goal_1, … until an index is missing.
        Each goal has sub-parameters: x, y, yaw.
        """
        waypoints = []
        idx = 0
        while True:
            prefix = f'goal_{idx}'
            try:
                self.declare_parameter(f'{prefix}.x')
                self.declare_parameter(f'{prefix}.y')
                self.declare_parameter(f'{prefix}.yaw')
            except rclpy.exceptions.ParameterAlreadyDeclaredException:
                pass

            try:
                x_param = self.get_parameter(f'{prefix}.x')
                y_param = self.get_parameter(f'{prefix}.y')
                yaw_param = self.get_parameter(f'{prefix}.yaw')
            except rclpy.exceptions.ParameterUninitializedException:
                break

            # Stop if parameters were not set (remain NOT_SET)
            if x_param.type_ == rclpy.Parameter.Type.NOT_SET:
                break

            x = float(x_param.value)
            y = float(y_param.value)
            yaw = float(yaw_param.value)

            if self._yaw_deg:
                yaw = math.radians(yaw)

            waypoints.append((x, y, yaw))
            self.get_logger().info(
                f'  goal_{idx}: x={x:.2f}, y={y:.2f}, yaw={math.degrees(yaw):.1f}°'
            )
            idx += 1

        return waypoints

    # ------------------------------------------------------------------ #
    #  Execution
    # ------------------------------------------------------------------ #
    def start(self) -> bool:
        """Wait for server and send the first goal."""
        self.get_logger().info('Waiting for action server...')
        if not self._client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Action server not available.')
            return False
        self.get_logger().info('Action server connected.')
        self._send_goal(self._index)
        return True

    def _send_goal(self, index: int) -> None:
        x, y, yaw = self._waypoints[index]

        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'odom'
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation = self._yaw_to_quaternion(yaw)

        goal = NavigateToPose.Goal()
        goal.goal_pose = pose

        self.get_logger().info(
            f'[{index + 1}/{len(self._waypoints)}] '
            f'Sending goal: x={x:.2f}, y={y:.2f}, yaw={math.degrees(yaw):.1f}°'
        )

        future = self._client.send_goal_async(
            goal,
            feedback_callback=self._feedback_cb,
        )
        future.add_done_callback(self._goal_response_cb)

    # ------------------------------------------------------------------ #
    #  Callbacks
    # ------------------------------------------------------------------ #
    def _goal_response_cb(self, future) -> None:
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Goal rejected.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted.')
        result_future = handle.get_result_async()
        result_future.add_done_callback(self._result_cb)

    def _feedback_cb(self, feedback_msg) -> None:
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'[{self._index + 1}/{len(self._waypoints)}] '
            f'{fb.current_state} — dist={fb.distance_to_goal:.2f} m',
            throttle_duration_sec=1.0,
        )

    def _result_cb(self, future) -> None:
        result = future.result().result
        prefix = f'[{self._index + 1}/{len(self._waypoints)}]'

        if result.success:
            self.get_logger().info(
                f'{prefix} ✓ Reached — '
                f'pos_err={result.final_position_error:.3f} m, '
                f'head_err={math.degrees(result.final_heading_error):.1f}°'
            )
            self._index += 1
            if self._index < len(self._waypoints):
                self._send_goal(self._index)
            else:
                self.get_logger().info('All waypoints completed.')
                rclpy.shutdown()
        else:
            self.get_logger().warning(
                f'{prefix} ✗ Failed — '
                f'pos_err={result.final_position_error:.3f} m, '
                f'head_err={math.degrees(result.final_heading_error):.1f}°'
            )
            rclpy.shutdown()

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _yaw_to_quaternion(yaw: float) -> Quaternion:
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw / 2.0)
        q.w = math.cos(yaw / 2.0)
        return q


def main(args=None):
    rclpy.init(args=args)
    try:
        node = GoToGoalClient()
    except RuntimeError as e:
        print(f'ERROR: {e}')
        rclpy.shutdown()
        return

    if node.start():
        rclpy.spin(node)

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
