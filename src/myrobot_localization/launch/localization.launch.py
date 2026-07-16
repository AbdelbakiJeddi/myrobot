import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    localization_pkg = get_package_share_directory("myrobot_localization")
    ekf_yaml = os.path.join(localization_pkg, "config", "ekf.yaml")

    mpu6050_node = Node(
        package="myrobot_localization",
        executable="mpu6050_driver.py",
        name="mpu6050_driver",
        output="screen",
    )

    robot_localization_ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[ekf_yaml],
    )

    return LaunchDescription([
        mpu6050_node,
        robot_localization_ekf,
    ])
