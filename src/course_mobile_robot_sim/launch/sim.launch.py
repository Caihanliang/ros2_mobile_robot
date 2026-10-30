from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = FindPackageShare('course_mobile_robot_sim')

    declare_model = DeclareLaunchArgument(
        'model',
        default_value='course_mobile_robot.urdf.xacro',
        description='Model filename inside the package urdf directory.',
    )

    model = LaunchConfiguration('model')
    use_rviz = LaunchConfiguration('use_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    initial_mode = LaunchConfiguration('initial_mode')

    world = PathJoinSubstitution([pkg, 'worlds', 'classroom_world.sdf'])
    model_path = PathJoinSubstitution([pkg, 'urdf', model])
    bridge_config = PathJoinSubstitution([pkg, 'config', 'bridge.yaml'])
    node_params = PathJoinSubstitution([pkg, 'config', 'sim_nodes.yaml'])
    rviz_config = PathJoinSubstitution([pkg, 'config', 'mobile_robot.rviz'])
    robot_description = ParameterValue(
        Command([FindExecutable(name='xacro'), ' ', model_path]),
        value_type=str,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            ])
        ),
        launch_arguments={
            'gz_args': ['-r -v 3 ', world],
            'on_exit_shutdown': 'true',
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time},
        ],
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[
            {'config_file': bridge_config},
            {'use_sim_time': use_sim_time},
        ],
    )

    # 从 robot_description 生成实体；Gazebo 内部把 URDF 转换为 SDF。
    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_spawn_model.launch.py',
            ])
        ),
        launch_arguments={
            'world': 'classroom_world',
            'topic': 'robot_description',
            'entity_name': 'course_mobile_robot',
            'allow_renaming': 'False',
            'x': '0.0',
            'y': '0.0',
            'z': '0.02',
        }.items(),
    )

    control_mode = Node(
        package='course_mobile_robot_sim',
        executable='control_mode_node',
        name='control_mode_node',
        output='screen',
        parameters=[{'initial_mode': initial_mode}],
    )

    safety = Node(
        package='course_mobile_robot_sim',
        executable='cmd_vel_safety_node',
        name='cmd_vel_safety_node',
        output='screen',
        parameters=[node_params],
    )

    front_distance = Node(
        package='course_mobile_robot_sim',
        executable='front_distance_node',
        name='front_distance_node',
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        declare_model,
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'initial_mode',
            default_value='MANUAL',
            description='MANUAL, CRUISE or NAVIGATION.',
        ),
        gazebo,
        robot_state_publisher,
        bridge,
        spawn,
        control_mode,
        safety,
        front_distance,
        rviz,
    ])
