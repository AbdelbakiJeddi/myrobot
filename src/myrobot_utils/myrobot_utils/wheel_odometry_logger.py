#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

WHEEL_RADIUS = 0.033
LEFT_JOINT = "left_wheel_joint"
RIGHT_JOINT = "right_wheel_joint"


class WheelDistanceLogger(Node):
    def __init__(self):
        super().__init__("wheel_distance_logger")
        self.declare_parameter("log_rate", 1.0)
        self.log_rate_ = float(self.get_parameter("log_rate").value)

        self.sub_ = self.create_subscription(
            JointState, "/joint_states", self.cb, 10)

        self.left_prev_ = None
        self.right_prev_ = None
        self.left_dist_ = 0.0
        self.right_dist_ = 0.0
        self.last_log_ = self.get_clock().now()

        self.create_timer(1.0 / self.log_rate_, self.log)

        self.get_logger().info(
            "Logging wheel travel distance. Drive the robot, then read the totals.")

    def cb(self, msg: JointState):
        try:
            li = msg.name.index(LEFT_JOINT)
            ri = msg.name.index(RIGHT_JOINT)
        except ValueError:
            self.get_logger().warn(f"Joint names not found. Available: {msg.name}", once=True)
            return

        left_pos = msg.position[li]
        right_pos = msg.position[ri]

        if self.left_prev_ is None:
            self.left_prev_ = left_pos
            self.right_prev_ = right_pos
            return

        self.left_dist_ += abs(left_pos - self.left_prev_) * WHEEL_RADIUS
        self.right_dist_ += abs(right_pos - self.right_prev_) * WHEEL_RADIUS
        self.left_prev_ = left_pos
        self.right_prev_ = right_pos

    def log(self):
        self.get_logger().info(
            f"Left: {self.left_dist_:.4f} m  |  Right: {self.right_dist_:.4f} m")


def main():
    rclpy.init()
    node = WheelDistanceLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()