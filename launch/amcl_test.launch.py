import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.substitutions import Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_rt = get_package_share_directory('drone_in_warehouse')  # 自己的 config_package
    auto_cafe_pkg = get_package_share_directory('auto_cafe')
    urdf_file_path = os.path.join(pkg_rt, 'models', 'x500', 'model.urdf.xacro')
    rviz_config = '/home/uni_co/ros2_ws/src/drone_in_warehouse/rviz/ks_warehouse.rviz'
    nav2_bringup_dir = os.path.join('/opt/ros/humble/share/nav2_bringup', 'launch')
    nav2_params = '/home/uni_co/ros2_ws/src/drone_in_warehouse/config/auto_cafe_bringup.yaml'
    map_file = '/home/uni_co/ros2_ws/src/drone_in_warehouse/maps/empty_warehouse.yaml'
    gazebo_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_rt, 'launch', 'diw_gz_sim.launch.py'))
    )

    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join('/home/uni_co/ros2_ws/src/drone_in_warehouse/launch', 'custom_bringup.launch.py'))
    )


    return LaunchDescription([
        gazebo_simulation,
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': ParameterValue(Command(['xacro ', urdf_file_path]),value_type=str ),
                'use_sim_time': True},
            ],
            remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
            ]
        ),

        # Node(
        #     package='robot_localization',
        #     executable='ekf_node',
        #     name='ekf_filter_node_odom',
        #     output='screen',
        #     parameters=['/home/uni_co/ros2_ws/src/drone_in_warehouse/config/ekf_param.yaml'],
        #     remappings=[
        #         ('odometry/filtered', '/odometry/odom')
        #     ]
        # ),

        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     name='static_tf_multiranger',
        #     output='screen',
        #     arguments=[
        #         '--x', '0.0',
        #         '--y', '0.0',
        #         '--z', '0.02',
        #         '--roll', '0.0',
        #         '--pitch', '0.0',
        #         '--yaw', '0.0',
        #         '--frame-id', 'crazyflie/base_footprint',
        #         '--child-frame-id', 'crazyflie/base_footprint/multiranger']
        # ),
        
        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     name='static_tf_imu',
        #     output='screen',
        #     arguments=[
        #         '--x', '0.0',
        #         '--y', '0.0',
        #         '--z', '0.0',
        #         '--roll', '0.0',
        #         '--pitch', '0.0',
        #         '--yaw', '0.0',
        #         '--frame-id', 'crazyflie/base_footprint',
        #         '--child-frame-id', 'crazyflie/base_footprint/imu']
        # ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_map',
            output='screen',
            arguments=[
                '--x', '0.0',
                '--y', '0.0',
                '--z', '0.0',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'map',
                '--child-frame-id', 'odom']
        ),


        # Node(
        #     package='nav2_map_server',
        #     executable='map_server',
        #     name='map_server',
        #     parameters=[{'yaml_filename': '/home/uni_co/ros2_ws/src/auto_cafe/maps/map.yaml'}]
        # ),

        # Node(
        #     package='nav2_lifecycle_manager',
        #     executable='lifecycle_manager',
        #     name='lifecycle_manager_map',
        #     parameters=[{
        #         'node_names': ['map_server'],
        #         'autostart': True
        #     }]
        # ),
        # Node(
        #         package='drone_in_warehouse',
        #         executable='command_combiner.py',
        #         name='command_combiner',
        #         output='screen'
        # ),

        # 開啟 rviz2
        Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config],    # 指定 rviz 的設定檔路徑
        ),

        TimerAction(
            period=5.0,
            actions=[bringup_launch,]
        )
    ])
