from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declare_model = DeclareLaunchArgument(
        'model',
        default_value='course_mobile_robot.urdf.xacro',
        description='Model filename inside the simulation package urdf directory.',
    )
    model = LaunchConfiguration('model')
    initial_mode = LaunchConfiguration('initial_mode')

    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('course_mobile_robot_sim'),
                'launch',
                'sim.launch.py',
            ])
        ),
        launch_arguments={
            'model': model,
            'initial_mode': initial_mode,
        }.items(),
    )
    applications = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('course_mobile_robot_apps'),
                'launch',
                'applications.launch.py',
            ])
        )
    )
    return LaunchDescription([
        declare_model,
        DeclareLaunchArgument(
            'initial_mode',
            default_value='CRUISE',
            description='MANUAL, CRUISE or NAVIGATION.',
        ),
        simulation,
        applications,
    ])
