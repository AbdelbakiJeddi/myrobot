import os
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    robot_description = ParameterValue(
        Command(
            [
                "xacro ",
                os.path.join(
                    get_package_share_directory("myrobot_description"),
                    "urdf",
                    "robot",
                    "my_robot.urdf.xacro",
                )
            ]
        ),
        value_type=str,
    )

    robot_state_publisher_node = Node(
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
            os.path.join(
                get_package_share_directory("myrobot_bringup"),
                "config",
                "controllers.yaml",
            ),
        ],
        output="screen",
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

    return LaunchDescription(
        [
            robot_state_publisher_node,
            controller_manager,
            joint_state_broadcaster_spawner,
            wheel_controller_spawner,
        ]
    )