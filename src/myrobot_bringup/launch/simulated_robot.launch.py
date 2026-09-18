import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # This bringup contains the arena, robot, controllers, camera bridge,
    # cmd_vel relay, and RViz. It does not start Nav2.
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory("myrobot_description"),
            "launch",
            "competition.launch.py",
        )),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", os.path.join(
            get_package_share_directory("myrobot_bringup"),
            "rviz",
            "vision_view.rviz",
        )],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )
    # Disabled: the diff-drive controller publishes the simulation odometry
    # directly on /odom and publishes the odom -> base_footprint TF.
    # robot_localization_ekf = Node(
    #     package="robot_localization",
    #     executable="ekf_node",
    #     name="ekf_filter_node",
    #     output="screen",
    #     parameters=[
    #         os.path.join(
    #             get_package_share_directory("myrobot_firmware"),
    #             "config",
    #             "ekf.yaml"),
    #         {"use_sim_time": True}
    #     ],
    # )
    return LaunchDescription([
        simulation,
        rviz,
    ])