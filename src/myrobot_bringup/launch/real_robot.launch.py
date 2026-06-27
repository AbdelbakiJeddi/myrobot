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
    # ── Launch arguments ──────────────────────────────────────────────
    use_nav_arg = DeclareLaunchArgument(
        "launch_navigation",
        default_value="false",
        description="Set to 'true' to also launch the go_to_goal navigation stack.",
    )
    launch_navigation = LaunchConfiguration("launch_navigation")

    # ── Paths ─────────────────────────────────────────────────────────
    description_pkg = get_package_share_directory("myrobot_description")
    controller_pkg = get_package_share_directory("myrobot_controller")
    firmware_pkg = get_package_share_directory("myrobot_firmware")
    navigation_pkg = get_package_share_directory("myrobot_navigation")

    # ── Robot description (URDF via xacro) ────────────────────────────
    robot_description = ParameterValue(
        Command([
            "xacro ",
            os.path.join(description_pkg, "urdf", "robot", "my_robot.urdf.xacro"),
        ]),
        value_type=str,
    )

    controllers_yaml = os.path.join(controller_pkg, "config", "myrobot_controllers.yaml")
    ekf_yaml = os.path.join(firmware_pkg, "config", "ekf.yaml")

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


    joint_state_broadcaster_spawner = TimerAction(
        period=3.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "joint_state_broadcaster",
                    "--controller-manager", "/controller_manager",
                ],
                output="screen",
            ),
        ],
    )

    wheel_controller_spawner = TimerAction(
        period=5.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                arguments=[
                    "myrobot_controller",
                    "--controller-manager", "/controller_manager",
                ],
                output="screen",
            ),
        ],
    )

    mpu6050_node = TimerAction(
        period=7.0,
        actions=[
            Node(
                package="myrobot_firmware",
                executable="mpu6050_driver.py",
                name="mpu6050_driver",
                output="screen",
            ),
        ],
    )

    robot_localization_ekf = TimerAction(
        period=9.0,
        actions=[
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node",
                output="screen",
                parameters=[ekf_yaml],
            ),
        ],
    )

    navigation = TimerAction(
        period=12.0,
        actions=[
            IncludeLaunchDescription(
                os.path.join(navigation_pkg, "launch", "go_to_goal.launch.py"),
            ),
        ],
        condition=IfCondition(launch_navigation),
    )

    # ── Assemble ──────────────────────────────────────────────────────
    return LaunchDescription([
        use_nav_arg,

        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
        mpu6050_node,
        robot_localization_ekf,
        navigation,
    ])
