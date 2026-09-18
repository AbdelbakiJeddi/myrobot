import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    myrobot_description = get_package_share_directory("myrobot_description")

    model_arg = DeclareLaunchArgument(
        name="model", default_value=os.path.join(myrobot_description, "urdf", "robot", "my_robot.urdf.xacro"),
        description="Absolute path to robot urdf file"
    )

    world_path = PathJoinSubstitution([
        myrobot_description,
        "worlds",
        "arena_world.sdf"
    ])

    model_path = myrobot_description

    gazebo_resource_path = SetEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        model_path
    )

    robot_description = ParameterValue(Command([
        "xacro ",
        LaunchConfiguration("model"),
        " is_sim:=true"
    ]), value_type=str)

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory("ros_gz_sim"), "launch"), "/gz_sim.launch.py"]),
        launch_arguments={
            "gz_args": [world_path, " -v 4 -r"]
        }.items()
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description",
                   "-name", "myrobot"],
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # IMU and LiDAR are intentionally disabled; the simulation uses
            # ros2_control odometry and the RGB camera only.
            # "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            # "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo",
        ],
    )

    controller = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory("myrobot_controller"),
                "launch",
                "controller.launch.py",
            )
        ])
    )

    twist_relay = Node(
        package="myrobot_controller",
        executable="twist_relay.py",
        name="twist_relay",
        output="screen",
    )


    return LaunchDescription([
        model_arg,
        gazebo_resource_path,
        robot_state_publisher_node,
        gazebo,
        gz_spawn_entity,
        gz_ros2_bridge,
        controller,
        twist_relay,
    ])