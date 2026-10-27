"""Start the simulator and the autonomy training nodes."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('cpu_sim', default_value='true'),
        DeclareLaunchArgument('human_gui', default_value='true'),
        DeclareLaunchArgument('cv_exposure', default_value='0.8'),
        DeclareLaunchArgument('foxglove', default_value='false'),
        DeclareLaunchArgument('foxglove_port', default_value='8765'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution([
                FindPackageShare('sim_node'), 'launch', 'sim_node_launch.py'
            ])),
            launch_arguments={
                'cpu_sim': LaunchConfiguration('cpu_sim'),
                'human_gui': LaunchConfiguration('human_gui'),
                'cv_exposure': LaunchConfiguration('cv_exposure'),
            }.items(),
        ),
        Node(package='sim_node', executable='keyboard_controls.py', output='screen'),
        Node(
            package='huskybot_cv', executable='huskybot_cv',
            parameters=[{'use_sim_time': True}], output='screen',
        ),
        Node(
            package='your_solution', executable='tf_broadcaster',
            parameters=[{'use_sim_time': True}], output='screen',
        ),
        Node(
            package='your_solution', executable='calc_error',
            parameters=[{'use_sim_time': True}], output='screen',
        ),
        Node(
            package='foxglove_bridge', executable='foxglove_bridge',
            parameters=[{'port': ParameterValue(
                LaunchConfiguration('foxglove_port'), value_type=int
            )}],
            condition=IfCondition(LaunchConfiguration('foxglove')),
            output='screen',
        ),
    ])
