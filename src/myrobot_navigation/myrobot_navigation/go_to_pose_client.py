#!/usr/bin/env python3

import math

from typing import Any, Dict, List

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter

from geometry_msgs.msg import PoseStamped, Quaternion
from myrobot_actions.action import NavigateToPose


def yaw_to_quaternion(yaw: float) -> Quaternion:
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class GoToPoseClient(Node):
    def __init__(self) -> None:
        super().__init__('go_to_pose_action_client')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._result_future = None
        self._declare_parameters()
        self._waypoints = self._load_waypoints_from_params()
        self._index = 0
        self._active_index = None

    def _declare_parameters(self) -> None:
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('yaw_deg', False)
        self.declare_parameter('waypoints_x', Parameter.Type.DOUBLE_ARRAY)
        self.declare_parameter('waypoints_y', Parameter.Type.DOUBLE_ARRAY)
        self.declare_parameter('waypoints_yaw', Parameter.Type.DOUBLE_ARRAY)
        self.declare_parameter('waypoints_frame_id',[''])
        self.declare_parameter('waypoints_yaw_deg', [False])

    def _load_waypoints_from_params(self) -> List[Dict[str, Any]]:
        default_frame = self.get_parameter('frame_id').value
        default_yaw_deg = bool(self.get_parameter('yaw_deg').value)

        xs_param = self.get_parameter('waypoints_x')
        ys_param = self.get_parameter('waypoints_y')
        yaws_param = self.get_parameter('waypoints_yaw')
        frames_raw = list(self.get_parameter('waypoints_frame_id').value)
        yaw_deg_raw = list(self.get_parameter('waypoints_yaw_deg').value)

        xs = list(xs_param.value) if xs_param.type_ != Parameter.Type.NOT_SET else []
        ys = list(ys_param.value) if ys_param.type_ != Parameter.Type.NOT_SET else []
        yaws = list(yaws_param.value) if yaws_param.type_ != Parameter.Type.NOT_SET else []
        frames = [] if frames_raw == [''] else frames_raw
        yaw_deg_flags = [] if yaw_deg_raw == [False] else yaw_deg_raw

        if not xs and not ys and not yaws:
            raise ValueError(
                'No waypoints provided. Set waypoints_x, waypoints_y, '
                'and waypoints_yaw parameters.'
            )

        if not (len(xs) == len(ys) == len(yaws)):
            raise ValueError('waypoints_x, waypoints_y, and waypoints_yaw must match in length.')

        if frames and len(frames) != len(xs):
            raise ValueError('waypoints_frame_id must be empty or match waypoint count.')

        if yaw_deg_flags and len(yaw_deg_flags) != len(xs):
            raise ValueError('waypoints_yaw_deg must be empty or match waypoint count.')

        normalized = []
        for index in range(len(xs)):
            frame_id = frames[index] if frames else default_frame
            yaw = float(yaws[index])
            yaw_deg = bool(yaw_deg_flags[index]) if yaw_deg_flags else default_yaw_deg
            if yaw_deg:
                yaw = math.radians(yaw)

            normalized.append(
                {
                    'x': float(xs[index]),
                    'y': float(ys[index]),
                    'yaw': yaw,
                    'frame_id': frame_id,
                }
            )

        return normalized

    def start(self) -> bool:
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Action server not available after waiting.')
            return False

        self.send_next_goal()
        return True

    def send_next_goal(self) -> None:
        if self._index >= len(self._waypoints):
            self.get_logger().info('All waypoints completed.')
            rclpy.shutdown()
            return

        waypoint = self._waypoints[self._index]
        self._active_index = self._index
        self._index += 1

        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = waypoint['frame_id']
        pose.pose.position.x = waypoint['x']
        pose.pose.position.y = waypoint['y']
        pose.pose.position.z = 0.0
        pose.pose.orientation = yaw_to_quaternion(waypoint['yaw'])

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info(
            f"[{self._active_index + 1}/{len(self._waypoints)}] "
            f"Sending goal: x={pose.pose.position.x:.2f}, "
            f"y={pose.pose.position.y:.2f}"
        )

        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback,
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted by server.')
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg) -> None:
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f"[{self._active_index + 1}/{len(self._waypoints)}] "
            f"Feedback: dist={feedback.distance_remaining:.2f} m, "
            f"angle={math.degrees(feedback.angle_remaining):.1f} deg, "
            f"elapsed={feedback.elapsed_time:.1f} s",
            throttle_duration_sec=1.0,
        )

    def result_callback(self, future) -> None:
        result = future.result().result
        prefix = f"[{self._active_index + 1}/{len(self._waypoints)}] "
        if result.success:
            self.get_logger().info(
                f"{prefix}Goal reached. Final distance={result.final_distance:.3f} m, "
                f"final angle error={math.degrees(result.final_angle_error):.2f} deg"
            )
            self.send_next_goal()
        else:
            self.get_logger().warning(
                f"{prefix}Goal failed. Final distance={result.final_distance:.3f} m, "
                f"final angle error={math.degrees(result.final_angle_error):.2f} deg"
            )
            rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    try:
        node = GoToPoseClient()
    except ValueError as exc:
        print(f"Failed to load waypoints from parameters: {exc}")
        rclpy.shutdown()
        return

    if node.start():
        rclpy.spin(node)
    else:
        rclpy.shutdown()

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
