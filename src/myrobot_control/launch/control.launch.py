from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation clock.',
    )

    control_file = LaunchConfiguration('control_file')
    control_file_arg = DeclareLaunchArgument(
        'control_file',
        default_value=FindPackageShare('myrobot_control').find('myrobot_control')
        + '/config/control_params.yaml',
        description='Path to GoToGoal controller parameters YAML.',
    )

    waypoints_file = LaunchConfiguration('waypoints_file')
    waypoints_file_arg = DeclareLaunchArgument(
        'waypoints_file',
        default_value=FindPackageShare('myrobot_control').find('myrobot_control')
        + '/config/waypoints.yaml',
        description='Path to waypoints YAML.',
    )

    server_node = Node(
        package='myrobot_control',
        executable='go_to_goal_server.py',
        name='go_to_goal_server',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            control_file,
        ],
    )

    client_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='myrobot_control',
                executable='go_to_goal_client.py',
                name='go_to_goal_client',
                output='screen',
                parameters=[
                    {'use_sim_time': use_sim_time},
                    waypoints_file,
                ],
            ),
        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        control_file_arg,
        waypoints_file_arg,
        server_node,
        client_node,
    ])
