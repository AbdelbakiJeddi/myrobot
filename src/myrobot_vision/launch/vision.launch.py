"""Launch the camera input node for the vision stack."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Create the configurable vision node launch description."""

    config_file = LaunchConfiguration("config_file")
    config_file_arg = DeclareLaunchArgument(
        "config_file",
        default_value=PathJoinSubstitution([
            FindPackageShare("myrobot_vision"),
            "config",
            "vision.yaml",
        ]),
        description="Path to vision node parameters.",
    )

    vision_node = Node(
        package="myrobot_vision",
        executable="vision_node.py",
        name="vision_node",
        output="screen",
        parameters=[config_file],
    )

    return LaunchDescription([config_file_arg, vision_node])
