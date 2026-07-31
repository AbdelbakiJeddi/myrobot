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

    madgwick_filter_node = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter_madgwick_node',
        output='screen',
        parameters=[{
            'use_mag': False,            # set True if you have a magnetometer
            'publish_tf': False,         # set True if you want it to publish a TF
            'world_frame': 'enu',        # 'enu', 'ned', or 'nwu'
            'fixed_frame': 'odom',
            'gain': 0.1,
            'zeta': 0.0,
        }],
        remappings=[
            ('imu/data', 'imu/out'),
        ]
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
