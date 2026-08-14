from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock.',
    )

    config_file = LaunchConfiguration('config_file')
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            FindPackageShare('myrobot_control'),
            'config', 'simple_navigator.yaml',
        ]),
        description='Path to simple_navigator parameters YAML.',
    )

    navigator_node = Node(
        package='myrobot_control',
        executable='simple_navigator.py',
        name='simple_navigator',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            config_file,
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        config_file_arg,
        navigator_node,
    ])