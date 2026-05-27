import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav = get_package_share_directory('myrobot_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time')
    map_yaml = LaunchConfiguration('map')

    # Paths to config files
    controller_yaml = os.path.join(pkg_nav, 'config', 'controller_server_blind.yaml')
    planner_yaml = os.path.join(pkg_nav, 'config', 'planner_server_blind.yaml')
    behavior_yaml = os.path.join(pkg_nav, 'config', 'behavior_server.yaml')
    smoother_yaml = os.path.join(pkg_nav, 'config', 'smoother_server.yaml')
    bt_navigator_yaml = os.path.join(pkg_nav, 'config', 'bt_navigator.yaml')

    # Path to custom behavior tree
    default_bt_xml = os.path.join(pkg_nav, 'behavior_tree', 'simple_navigation.xml')

    lifecycle_nodes = [
        'map_server',
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'bt_navigator'
    ]

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false',
                              description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument('map', default_value=os.path.join(pkg_nav, 'maps', 'blank_map.yaml'),
                              description='Full path to the map yaml file to load'),

        # --- Static TF: map -> odom ---
        # Bridges the map and odom frames so Nav2 can plan globally
        # without a localization node (AMCL). The robot's starting position
        # in the map frame equals its odom origin.
        Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_map_odom_publisher",
        output="screen",
        arguments=["--x", "0", "--y", "0", "--z", "0",
           "--roll", "0", "--pitch", "0", "--yaw", "0",
           "--frame-id", "map", "--child-frame-id", "odom"],
        parameters=[{"use_sim_time": use_sim_time}]),
        # --- Map Server ---
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'yaml_filename': map_yaml},
                        {'use_sim_time': use_sim_time}]),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            remappings=[('cmd_vel', '/myrobot_controller/cmd_vel'),],
            parameters=[controller_yaml, {'use_sim_time': use_sim_time}]),

         Node(
             package='nav2_smoother',
             executable='smoother_server',
             name='smoother_server',
             output='screen',
             parameters=[smoother_yaml, {'use_sim_time': use_sim_time}]),

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[planner_yaml, {'use_sim_time': use_sim_time}]),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[behavior_yaml, {'use_sim_time': use_sim_time}]),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[
                bt_navigator_yaml,
                {'use_sim_time': use_sim_time},
            ]),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': True},
                        {'node_names': lifecycle_nodes}])
    ])