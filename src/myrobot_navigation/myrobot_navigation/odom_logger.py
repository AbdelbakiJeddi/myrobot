#!/usr/bin/env python3
"""Simple node that subscribes to odom and logs x, y, yaw."""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math


class OdomLogger(Node):
    """Subscribe to odom and log x, y, yaw."""

    def __init__(self):
        super().__init__('odom_logger')
        self.subscription = self.create_subscription(
            Odometry,
            '/odometry/filtered',
            self.odom_callback,
            10
        )
        self.subscription

    def odom_callback(self, msg: Odometry) -> None:
        """Log x, y, yaw from odom message."""
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Extract yaw from quaternion
        orientation = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
            1.0 - 2.0 * (orientation.y * orientation.y + orientation.z * orientation.z)
        )
        yaw_de = math.degrees(yaw)
        self.get_logger().info(f'x={x:.3f}, y={y:.3f}, yaw={yaw_de:.1f}°')


def main() -> None:
    """Entry point for the odom_logger node."""
    rclpy.init()
    node = OdomLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
