# 用來開啟 Gazebo 模擬與 ROS2 橋接器的檔案

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    # 此 Launch檔的初始參數，用來設定是否需要顯示 GAZEBO GUI 介面
    declare_gui = DeclareLaunchArgument(
        'use_gui',
        default_value='true'
    )

    use_gui = LaunchConfiguration('use_gui')
    
    # Setup project paths
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_dir = get_package_share_directory('drone_in_warehouse')

    # 讓 Gazebo 能找到 drone_in_warehouse 的模型資料夾（不含硬編碼路徑）
    gz_models_path = os.path.join(pkg_dir, 'models')
    existing_gz_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    full_gz_resource_path = gz_models_path + (':' + existing_gz_path if existing_gz_path else '')
    set_gz_resource_path = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', full_gz_resource_path)

    # Determine gz_settings at launch time using substitution:
    # use_gui=='false' -> '-r -s' (headless, server only)
    # use_gui=='true'  -> '-r' (with GUI)
    gz_settings = PythonExpression([
        "'-r -s' if '", use_gui, "' == 'false' else '-r'"
    ])

    # Setup to launch the simulator and Gazebo world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': [
                os.path.join(pkg_dir, 'worlds', 'ks_warehouse_simple.sdf'),
                ' ',
                gz_settings,
            ]}.items(),
    )

    # GAZEBO 和 ROS2 橋接節點
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_dir, 'config', 'ros_gz_bridge.yaml'),
            'use_sim_time': True,
        }],

        output='screen'
    )

    return LaunchDescription([
        set_gz_resource_path,
        declare_gui,
        gz_sim,
        bridge,
    ])