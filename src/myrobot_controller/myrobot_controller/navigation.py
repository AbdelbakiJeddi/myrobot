#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math

class Navigator(Node):
    def __init__(self):
        super().__init__('navigator')
        self.declare_parameter('linear_velocity', 0.2)
        self.declare_parameter('angular_velocity', 0.5)
        self.linear_velocity = self.get_parameter('linear_velocity').value
        self.angular_velocity = self.get_parameter('angular_velocity').value
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.odom_subscriber = self.create_subscription(Odometry, 'odom', self.odom_callback, 10)
        self.get_logger().info('Navigation Node is active, ready to navigate!')
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

    def euler_from_quaternion(self, x, y, z, w):
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
        return yaw_z

    def GoToPose(self, distance):
        twist = Twist()
        twist.linear.x = self.linear_velocity
        twist.angular.z = 0.0

        # Record start position
        start_x = self.x
        start_y = self.y

        # Calculate target position (simple forward motion)
        target_distance = abs(distance)
        direction = 1.0 if distance >= 0 else -1.0

        self.get_logger().info('GoToPose: starting, target_distance={:.2f}m'.format(target_distance))

        while True:
            # Calculate current distance traveled
            dx = self.x - start_x
            dy = self.y - start_y
            traveled = math.sqrt(dx*dx + dy*dy)

            if traveled >= target_distance:
                break

            self.cmd_vel_publisher.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(0.01)

        stop_msg = Twist()
        self.cmd_vel_publisher.publish(stop_msg)
        self.get_logger().info('GoToPose: completed, traveled={:.2f}m'.format(traveled))

    def Rotate(self, angle):
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = self.angular_velocity if angle > 0 else -self.angular_velocity

        # Record start yaw
        start_yaw = self.yaw
        target_yaw = start_yaw + angle
        direction = 1.0 if angle >= 0 else -1.0

        self.get_logger().info('Rotate: starting, target_angle={:.2f} rad'.format(abs(angle)))

        while True:
            # Calculate current rotation
            current_yaw = self.yaw
            # Handle angle wrapping
            delta_yaw = current_yaw - start_yaw
            rotated = abs(delta_yaw)

            if rotated >= abs(angle):
                break

            self.cmd_vel_publisher.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.01)
            time.sleep(0.01)

        stop_msg = Twist()
        self.cmd_vel_publisher.publish(stop_msg)
        self.get_logger().info('Rotate: completed, rotated={:.2f} rad'.format(rotated))

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        orientation_q = msg.pose.pose.orientation
        self.yaw = self.euler_from_quaternion(orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w)
        self.get_logger().info('Odom: x={:.2f}, y={:.2f}, yaw={:.2f}'.format(self.x, self.y, self.yaw))

def main():
    rclpy.init()
    node = Navigator()
    
    time.sleep(2.0)
    
    for i in range(4):
        node.GoToPose(1.0) 
        node.Rotate(1.5708) 
        
    node.GoToPose(1.0) 
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()