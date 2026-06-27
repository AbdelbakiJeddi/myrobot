#!/usr/bin/env python3

# Python header
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

# ROS header
import rclpy
from rclpy.node import Node
# ADD THIS IMPORT:
from ament_index_python.packages import get_package_share_directory

class Visual(Node):        
    def __init__(self):
        # Initialize the node properly
        super().__init__('path_visual')

        # Dynamically find the package's install/share directory
        # (Replace 'myrobot_navigation' with your actual package name if different)
        package_share_dir = get_package_share_directory('myrobot_navigation')
        file_arg = self.declare_parameter('waypoints_file', 'waypoints/0_track.csv').get_parameter_value().string_value
        # Point directly to where the waypoints folder is
        filename = os.path.join(package_share_dir, 'waypoints', file_arg)

        try:
            with open(filename) as f:
                path_points = [tuple(line) for line in csv.reader(f)]
            
            path_points.pop(0)
            path_points_x       = np.array([float(point[0]) for point in path_points])
            path_points_y       = np.array([float(point[1]) for point in path_points])
            path_points_heading = np.array([float(point[2]) for point in path_points])
            
            # Setup side-by-side or separate plots to fix the overlapping issue!
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
    path_visual = Visual()
    # Note: plt.show() will still block spin here, but the file will load!
    rclpy.spin(path_visual)
    path_visual.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()