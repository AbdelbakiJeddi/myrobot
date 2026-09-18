#!/usr/bin/env python3
"""Camera input node for the myrobot vision stack."""

from time import monotonic

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class VisionNode(Node):
    """Receive camera frames and provide a stable hook for vision algorithms."""

    def __init__(self) -> None:
        super().__init__("vision_node")

        self.declare_parameter("image_topic", "/camera/image_raw")
        self.declare_parameter("queue_depth", 5)
        self.declare_parameter("log_every_n_frames", 30)

        image_topic = str(self.get_parameter("image_topic").value)
        queue_depth = int(self.get_parameter("queue_depth").value)
        self._log_every_n_frames = max(
            1, int(self.get_parameter("log_every_n_frames").value)
        )

        self._bridge = CvBridge()
        self._frame_count = 0
        self._last_frame_time = 0.0
        self._image_sub = self.create_subscription(
            Image,
            image_topic,
            self._image_callback,
            queue_depth,
        )

        self.get_logger().info(f"Vision node listening on {image_topic}")

    def _image_callback(self, message: Image) -> None:
        try:
            frame = self._bridge.imgmsg_to_cv2(message, desired_encoding="bgr8")
        except Exception as error:
            self.get_logger().error(f"Could not convert camera frame: {error}")
            return

        self._frame_count += 1
        now = monotonic()
        if self._frame_count % self._log_every_n_frames == 0:
            elapsed = now - self._last_frame_time if self._last_frame_time else 0.0
            fps = self._log_every_n_frames / elapsed if elapsed > 0.0 else 0.0
            self.get_logger().info(
                f"Received frame {self._frame_count}: "
                f"{frame.shape[1]}x{frame.shape[0]} at {fps:.1f} Hz"
            )
            self._last_frame_time = now


def main(args=None) -> None:
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
