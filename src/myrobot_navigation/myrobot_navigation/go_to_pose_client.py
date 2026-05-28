#!/usr/bin/env python3

import argparse
import math

from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover - handled at runtime
    yaml = None

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

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
    def __init__(self, waypoints: List[Dict[str, Any]]) -> None:
        super().__init__('go_to_pose_action_client')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._result_future = None
        self._waypoints = waypoints
        self._index = 0
        self._active_index = None

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


def load_waypoints(
    path: str,
    default_frame: str,
    default_yaw_deg: bool,
) -> List[Dict[str, Any]]:
    if yaml is None:
        raise RuntimeError('PyYAML is required: sudo apt install python3-yaml')

    with open(path, 'r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle)

    if data is None:
        raise ValueError('YAML file is empty.')

    if isinstance(data, dict):
        default_frame = data.get('frame_id', default_frame)
        default_yaw_deg = bool(data.get('yaw_deg', default_yaw_deg))
        waypoints = data.get('waypoints', [])
    elif isinstance(data, list):
        waypoints = data
    else:
        raise ValueError('YAML must be a list or contain a waypoints list.')

    if not waypoints:
        raise ValueError('No waypoints found in YAML.')

    normalized = []
    for index, waypoint in enumerate(waypoints, start=1):
        if not isinstance(waypoint, dict):
            raise ValueError(f'Waypoint {index} must be a mapping.')

        if 'x' not in waypoint or 'y' not in waypoint or 'yaw' not in waypoint:
            raise ValueError(f'Waypoint {index} must include x, y, and yaw.')

        frame_id = waypoint.get('frame_id', default_frame)
        yaw_deg = bool(waypoint.get('yaw_deg', default_yaw_deg))
        yaw = float(waypoint['yaw'])
        if yaw_deg:
            yaw = math.radians(yaw)

        normalized.append(
            {
                'x': float(waypoint['x']),
                'y': float(waypoint['y']),
                'yaw': yaw,
                'frame_id': frame_id,
            }
        )

    return normalized


def parse_args():
    parser = argparse.ArgumentParser(
        description='Send a NavigateToPose goal to the action server.'
    )
    parser.add_argument('--yaml', dest='yaml_path', help='Path to YAML waypoints file')
    parser.add_argument('x', type=float, nargs='?', help='Target X in meters')
    parser.add_argument('y', type=float, nargs='?', help='Target Y in meters')
    parser.add_argument('yaw', type=float, nargs='?', help='Target yaw (rad by default)')
    parser.add_argument('--deg', action='store_true', help='Yaw is in degrees')
    parser.add_argument('--frame', default='odom', help='Frame ID for the goal')
    return parser.parse_args()


def main(args=None) -> None:
    parsed = parse_args()

    if parsed.yaml_path:
        try:
            waypoints = load_waypoints(parsed.yaml_path, parsed.frame, parsed.deg)
        except (ValueError, RuntimeError) as exc:
            print(f"Failed to load waypoints: {exc}")
            return
    else:
        if parsed.x is None or parsed.y is None or parsed.yaw is None:
            print('Provide x y yaw or use --yaml <file>.')
            return
        yaw = math.radians(parsed.yaw) if parsed.deg else parsed.yaw
        waypoints = [
            {
                'x': parsed.x,
                'y': parsed.y,
                'yaw': yaw,
                'frame_id': parsed.frame,
            }
        ]

    rclpy.init(args=args)
    node = GoToPoseClient(waypoints)

    if node.start():
        rclpy.spin(node)
    else:
        rclpy.shutdown()

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
