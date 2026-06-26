#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

WHEEL_RADIUS = 0.033  # meters — adjust to your wheel radius

LEFT_JOINT  = "left_wheel_joint"   # adjust to your joint names
RIGHT_JOINT = "right_wheel_joint"

class WheelDistanceLogger(Node):
    def __init__(self):
        super().__init__("wheel_distance_logger")
        self.sub_ = self.create_subscription(
            JointState, "/joint_states", self.cb, 10
        )
        self.left_start_  = None
        self.right_start_ = None
        self.get_logger().info("Waiting for joint states…")

    def cb(self, msg: JointState):
        try:
            li = msg.name.index(LEFT_JOINT)
            ri = msg.name.index(RIGHT_JOINT)
        except ValueError:
            self.get_logger().warn(f"Joint names not found. Available: {msg.name}", once=True)
            return

        left_pos  = msg.position[li]
        right_pos = msg.position[ri]

        if self.left_start_ is None:
            self.left_start_  = left_pos
            self.right_start_ = right_pos
            self.get_logger().info("Reference set — logging distance from this point.")
            return

        left_dist  = (left_pos  - self.left_start_)  * WHEEL_RADIUS
        right_dist = (right_pos - self.right_start_) * WHEEL_RADIUS

        self.get_logger().info(
            f"Left: {left_dist:+.4f} m  |  Right: {right_dist:+.4f} m  |  "
            f"Diff: {abs(left_dist - right_dist):.4f} m"
        )

def main():
    rclpy.init()
    node = WheelDistanceLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()