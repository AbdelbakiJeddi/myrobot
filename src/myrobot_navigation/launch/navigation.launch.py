from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    waypoints_file = LaunchConfiguration('waypoints_file')

    waypoints_file_args = DeclareLaunchArgument(
        'waypoints_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare('myrobot_navigation'), 'config', 'waypoints.yaml']
        ),
        description='Path to the go_to_pose_client parameters YAML.',
    )

    go_to_pose_server = Node(
        package='myrobot_navigation',
        executable='go_to_pose_action.py',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )
    go_to_pose_client = Node(
        package='myrobot_navigation',
        executable='go_to_pose_client.py',
        output='screen',
        parameters=[{'use_sim_time': True}, waypoints_file],
    )

    return LaunchDescription(
        [
            waypoints_file_args,
            go_to_pose_server,
            go_to_pose_client,
        ]
    )
