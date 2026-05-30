import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    hardware_interface = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("myrobot_firmware"),
            "launch",
            "hardware_interface.launch.py"
        )
    )

    controller = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("myrobot_controller"),
            "launch",
            "controller.launch.py"
        )
    )
    navigation = IncludeLaunchDescription(
        os.path.join(
            get_package_share_directory("myrobot_navigation"),
            "launch",
            "go_to_goal.launch.py"
        )
    )

        
    return LaunchDescription([

        hardware_interface,
        controller,
        navigation
    ])
