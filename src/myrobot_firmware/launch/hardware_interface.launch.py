import os
from launch import LaunchDescription
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
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[
            {"robot_description": robot_description},
            os.path.join(
                get_package_share_directory("myrobot_controller"),
                "config",
                "myrobot_controllers.yaml",
            ),
        ]
    )

    mpu6050_node = Node(
        package="myrobot_firmware",
        executable="mpu6050_driver.py",
        name="mpu6050_driver",
        output="screen",
    )

    robot_localization_ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(
                get_package_share_directory("myrobot_firmware"),
                "config",
                "ekf.yaml")
        ],
    )

    return LaunchDescription(
        [
            robot_state_publisher_node,
            controller_manager,
            mpu6050_node,
            robot_localization_ekf,
        ]
    )