import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """
    Real-robot bringup with sequenced node startup.
    """
    use_nav_arg = DeclareLaunchArgument(
        "launch_navigation",
        default_value="false",
        description="Set to 'true' to also launch the go_to_goal navigation stack.",
    )
    launch_navigation = LaunchConfiguration("launch_navigation")

    description_pkg = get_package_share_directory("myrobot_description")
    controller_pkg = get_package_share_directory("myrobot_bringup")
    navigation_pkg = get_package_share_directory("myrobot_control")

    robot_description = ParameterValue(
        Command([
            "xacro ",
            os.path.join(description_pkg, "urdf", "robot", "my_robot.urdf.xacro"),
        ]),
        value_type=str,
    )

    controllers_yaml = os.path.join(controller_pkg, "config", "controllers.yaml")
    ekf_yaml = os.path.join(
        get_package_share_directory("myrobot_localization"), "config", "ekf.yaml")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description},
            controllers_yaml,
        ],
        output="screen",
    )

    # Bridge /cmd_vel → /myrobot_controller/cmd_vel (TwistStamped)
    twist_relay = TimerAction(
        period=6.0,
        actions=[
            Node(
                package="myrobot_control",
                executable="twist_relay.py",
                name="twist_relay",
                output="screen",
            ),
        ],
    )

    joint_state_broadcaster_spawner = TimerAction(
        period=2.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "joint_state_broadcaster",
                    "--controller-manager", "/controller_manager",
                    "--controller-manager-timeout", "30",
                ],
                output="screen",
            ),
        ],
    )

    wheel_controller_spawner = TimerAction(
        period=4.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "myrobot_controller",
                    "--controller-manager", "/controller_manager",
                    "--controller-manager-timeout", "30",
                ],
                output="screen",
            ),
        ],
    )

    localization = TimerAction(
        period=8.0,
        actions=[
            IncludeLaunchDescription(
                os.path.join(
                    get_package_share_directory("myrobot_localization"),
                    "launch", "localization.launch.py"),
            ),
        ],
    )

    navigation = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                os.path.join(navigation_pkg, "launch", "control.launch.py"),
            ),
        ],
        condition=IfCondition(launch_navigation),
    )

    return LaunchDescription([
        use_nav_arg,

        robot_state_publisher,
        controller_manager,
        twist_relay,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
        localization,
        navigation,
    ])
