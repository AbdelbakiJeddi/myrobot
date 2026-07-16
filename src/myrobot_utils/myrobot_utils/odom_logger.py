#!/usr/bin/env python3
"""Simple node that subscribes to odom and logs x, y, yaw."""

import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class OdomLogger(Node):
    """Subscribe to odom and log x, y, yaw."""

    def __init__(self):
        super().__init__("odom_logger")
        self.declare_parameter("odom_topic", "/odometry/filtered")
        self.subscription = self.create_subscription(
            Odometry, self.get_parameter("odom_topic").value, self.odom_callback, qos_profile_sensor_data
        )

    def odom_callback(self, msg: Odometry) -> None:
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        orientation = msg.pose.pose.orientation
        yaw = math.atan2(
            2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
            1.0 - 2.0 * (orientation.y * orientation.y + orientation.z * orientation.z),
        )
        self.get_logger().info(f"x={x:.3f}, y={y:.3f}, yaw={math.degrees(yaw):.1f}°")


def main() -> None:
    rclpy.init()
    node = OdomLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
