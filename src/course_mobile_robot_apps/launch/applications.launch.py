from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('course_mobile_robot_apps'),
        'config',
        'application_nodes.yaml',
    ])

    return LaunchDescription([
        Node(
            package='course_mobile_robot_apps',
            executable='simple_cruise_node',
            name='simple_cruise_node',
            output='screen',
            parameters=[params],
        ),
        Node(
            package='course_mobile_robot_apps',
            executable='simple_goal_navigation_node',
            name='simple_goal_navigation_node',
            output='screen',
            parameters=[params],
        ),
    ])
