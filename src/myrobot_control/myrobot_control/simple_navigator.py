#!/usr/bin/env python3
"""
Simple Navigator — open-loop square-path test using EKF-filtered odometry.

Unlike the original navigation.py, this node:
  - Subscribes to /odometry/filtered (not raw /odom) for accurate pose
  - Handles angle wrapping correctly in Rotate()
  - Uses normalize() consistently so yaw errors never jump at ±π

This is a diagnostic/example node; for real navigation use the
GoToGoal action server (go_to_goal_server.py).
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math


class Navigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')
        self.declare_parameter('linear_velocity', 0.2)
        self.declare_parameter('angular_velocity', 0.5)
        self.linear_velocity = self.get_parameter('linear_velocity').value
        self.angular_velocity = self.get_parameter('angular_velocity').value
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.odom_subscriber = self.create_subscription(
            Odometry, '/odometry/filtered', self.odom_callback, 10)
        self.get_logger().info('Simple Navigator ready (EKF-filtered odometry).')
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

    @staticmethod
    def normalize(angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return math.atan2(math.sin(angle), math.cos(angle))

    def euler_from_quaternion(self, x, y, z, w):
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        return math.atan2(t3, t4)

    def GoToPose(self, distance):
        twist = Twist()
        twist.linear.x = self.linear_velocity * (1.0 if distance >= 0 else -1.0)
        twist.angular.z = 0.0

        start_x = self.x
        start_y = self.y
        target_distance = abs(distance)

        self.get_logger().info('GoToPose: target={:.2f}m'.format(target_distance))

        while rclpy.ok():
            dx = self.x - start_x
            dy = self.y - start_y
            traveled = math.sqrt(dx * dx + dy * dy)
            if traveled >= target_distance:
                break
            self.cmd_vel_publisher.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(0.01)

        self.cmd_vel_publisher.publish(Twist())
        self.get_logger().info('GoToPose: done, traveled={:.2f}m'.format(traveled))

    def Rotate(self, angle):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = self.angular_velocity if angle > 0 else -self.angular_velocity

        start_yaw = self.yaw
        target_yaw = start_yaw + angle

        self.get_logger().info('Rotate: target={:.2f}rad'.format(abs(angle)))

        while rclpy.ok():
            # Normalized remaining rotation avoids ±π wrap discontinuity
            remaining = self.normalize(target_yaw - self.yaw)
            if abs(remaining) < 0.02:
                break
            self.cmd_vel_publisher.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(0.01)

        self.cmd_vel_publisher.publish(Twist())
        self.get_logger().info('Rotate: done, rotated={:.2f}rad'.format(
            abs(self.normalize(self.yaw - start_yaw))))

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.yaw = self.euler_from_quaternion(q.x, q.y, q.z, q.w)


def main():
    rclpy.init()
    node = Navigator()
    time.sleep(2.0)
    for _ in range(4):
        node.GoToPose(1.0)
        node.Rotate(1.5708)
    node.GoToPose(1.0)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
