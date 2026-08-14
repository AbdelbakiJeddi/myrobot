import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    Command,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Real-robot bringup entrypoint.

    No magic timers: the controller spawners self-wait on the controller
    manager (--controller-manager-timeout). Navigation is gated on an
    event: it only starts after `ros2 topic wait` sees the first
    /odometry/filtered message from the EKF.
    """
    use_nav_arg = DeclareLaunchArgument(
        "launch_navigation",
        default_value="false",
        description="Set to 'true' to also launch the navigation stack.",
    )
    launch_navigation = LaunchConfiguration("launch_navigation")

    robot_description = ParameterValue(
        Command([
            "xacro ",
            PathJoinSubstitution([
                FindPackageShare("myrobot_description"),
                "urdf", "robot", "my_robot.urdf.xacro",
            ]),
        ]),
        value_type=str,
    )

    controllers_yaml = PathJoinSubstitution([
        FindPackageShare("myrobot_bringup"),
        "config", "controllers.yaml",
    ])

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
    twist_relay = Node(
        package="myrobot_control",
        executable="twist_relay.py",
        name="twist_relay",
        output="screen",
    )

    # Spawners self-wait on the controller manager (no timer needed).
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "30",
        ],
        output="screen",
    )

    wheel_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "myrobot_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "30",
        ],
        output="screen",
    )

    localization = IncludeLaunchDescription(
        PathJoinSubstitution([
            FindPackageShare("myrobot_localization"),
            "launch", "localization.launch.py",
        ]),
    )

    # Block until the EKF publishes its first filtered odometry message,
    # then start navigation. Exits 0 when the topic has a message.
    wait_for_odom = ExecuteProcess(
        cmd=["ros2", "topic", "wait", "/odometry/filtered"],
        output="screen",
    )

    navigation = IncludeLaunchDescription(
        PathJoinSubstitution([
            FindPackageShare("myrobot_control"),
            "launch", "control.launch.py",
        ]),
        condition=IfCondition(launch_navigation),
    )

    start_navigation_after_odom = RegisterEventHandler(
        OnProcessExit(
            target_action=wait_for_odom,
            on_exit=[navigation],
        )
    )

    return LaunchDescription([
        use_nav_arg,
        robot_state_publisher,
        controller_manager,
        twist_relay,
        joint_state_broadcaster_spawner,
        wheel_controller_spawner,
        localization,
        wait_for_odom,
        start_navigation_after_odom,
    ])