from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # SLAM 保持为独立扩展，需要时在仿真启动后单独运行。
    params = PathJoinSubstitution([
        FindPackageShare('course_mobile_robot_sim'),
        'config',
        'slam_toolbox.yaml',
    ])

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('slam_toolbox'),
                'launch',
                'online_async_launch.py',
            ])
        ),
        launch_arguments={
            'slam_params_file': params,
            'use_sim_time': 'true',
        }.items(),
    )

    return LaunchDescription([slam])
