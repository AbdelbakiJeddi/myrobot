#!/usr/bin/env python3

import os
import csv
import numpy as np
import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory


class PathVisualizer(Node):
    """Offline tool: plot a track CSV from the waypoints/ folder."""

    def __init__(self):
        super().__init__('path_visualizer')
        package_share_dir = get_package_share_directory('myrobot_utils')
        file_arg = self.declare_parameter(
            'waypoints_file', '0_track.csv').get_parameter_value().string_value
        filename = os.path.join(package_share_dir, '..', '..', '..',
                                'myrobot_bringup', 'waypoints', file_arg)

        try:
            with open(filename) as f:
                path_points = [tuple(line) for line in csv.reader(f)]

            path_points.pop(0)
            path_points_x = np.array([float(p[0]) for p in path_points])
            path_points_y = np.array([float(p[1]) for p in path_points])
            path_points_heading = np.array([float(p[2]) for p in path_points])

            plt.figure(1)
            plt.scatter(path_points_x, path_points_y, color='blue', label='Track')
            plt.xlim([-10, 70])
            plt.ylim([-40, 40])
            plt.title("2D Track Map (Meters)")
            plt.grid(True)

            plt.figure(2)
            plt.plot(path_points_heading, color='red', label='Heading')
            plt.title("Heading (Yaw) over Time")
            plt.grid(True)

            plt.show()

        except FileNotFoundError:
            self.get_logger().error(f"Could not find CSV file at: {filename}")


def main(args=None):
    rclpy.init(args=args)
    node = PathVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
