from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
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

    waypoints_file = LaunchConfiguration('waypoints_file')
    waypoints_file_arg = DeclareLaunchArgument(
        'waypoints_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare('myrobot_navigation'), 'config', 'waypoints.yaml']
        ),
        description='Path to waypoints YAML.',
    )

    controller_file = LaunchConfiguration('controller_file')
    controller_file_arg = DeclareLaunchArgument(
        'controller_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare('myrobot_navigation'), 'config', 'controller.yaml']
        ),
        description='Path to controller parameters YAML.',
    )

    # -- nodes --
    server_node = Node(
        package='myrobot_navigation',
        executable='go_to_goal_server.py',
        name='go_to_goal_server',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            controller_file,
        ],
    )

    # Give the action server 2 s to start before the client tries to connect.
    # The client has its own wait_for_server(timeout_sec=10), but launching
    # it too early can cause it to miss the server registration entirely.
    client_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='myrobot_navigation',
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
        waypoints_file_arg,
        controller_file_arg,
        server_node,
        client_node,
    ])
