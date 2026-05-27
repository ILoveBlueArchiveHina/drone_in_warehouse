import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    diw_pkg = get_package_share_directory('drone_in_warehouse')
    mavros = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(diw_pkg , 'launch', 'mavros.launch.py')))

    return LaunchDescription([
        mavros,
        TimerAction(
            period = 3.0,
            actions = [
                Node(
                    package='unico_pack',
                    executable='main.py',
                    output='screen',
                    parameters=[{
                        'home_pose_x': 16.3,
                        'home_pose_y': 8.7,
                        'rosbag_folder_path': '/home/uni_co/rosbag',
                        'mqtt_broker': 'broker.emqx.io',
                        "use_sim_time": True,
                    }]
                )
            ]
        ),
        

        TimerAction(
        period = 3.0,
        actions = [
            Node(
            package='unico_pack',
            executable='mission_dispatcher_v4.py',
            output='screen',
            )]
        ),
        

        TimerAction(
        period = 6.0,
        actions = [
            Node(
                package='unico_pack',
                executable='cmd_vel_bridge',
            ),
            Node(
                package='unico_pack',
                executable='velocity_controller',
            )
            ]
        ),
    ])
