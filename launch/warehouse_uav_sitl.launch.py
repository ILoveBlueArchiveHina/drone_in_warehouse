# 開啟 GAZEBO SITL 和 NAV2
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.substitutions import Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    diw_pkg_path = get_package_share_directory('drone_in_warehouse')  # SITL ros2 套件包位置(share 路徑)
    unico_pack_path = get_package_share_directory('unico_pack')

    urdf_file_path = os.path.join(diw_pkg_path, 'models', 'x500', 'model.urdf.xacro')         # 飛機的結構描述檔案
    rviz_config = os.path.join(diw_pkg_path, 'rviz', 'ks_warehouse.rviz')  # rviz2可視化界面設定檔案
    nav2_params = os.path.join(unico_pack_path, 'config', 'mppi_orientation_control.yaml')   # 導航要用到的參數檔案位置
    map_file = os.path.join(diw_pkg_path, 'maps', 'empty_warehouse.yaml')  # 導航要用到的2d地圖檔案位置
    bt_xml = os.path.join(unico_pack_path, 'config', 'drone_nav_face_target.xml') 
    
    # gazebo模擬
    gazebo_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(diw_pkg_path, 'launch', 'warehouse_gz_sim.launch.py')),
        launch_arguments={
            'use_gui': 'false',  # 如果希望模擬時電腦跑得順暢，可以設為false，這樣會關掉 gazebo畫面省資源。
        }.items()
    )

    # 導航
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(unico_pack_path, 'launch', 'nav2_bringup.launch.py')),
        launch_arguments={
            'map_file': map_file,
            'params_file': nav2_params,
            'bt_xml': bt_xml,
            'user': "uni_co",
            'use_sim_time': 'true',
            'map_odom_tf_x': '27.4',
            'map_odom_tf_y': '-16.3',
            'map_odom_tf_z': '0.0',
            'map_odom_tf_yaw': '-1.5707963'
        }.items()
    )

    manager_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(diw_pkg_path, 'launch', 'manager_system_bringup_sitl.launch.py')))



    return LaunchDescription([
        manager_launch, # 開啟管理節點launch
        
        Node(   # 開啟 rviz2，可視化圖形介面
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config],    # 指定 rviz 的設定檔路徑
        ),

        
        Node(   # 啟動機器人動態發布節點，用來告訴ros2 飛機的結構
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

        # 啟動gazebo模擬
        TimerAction(
            period=7.0,
            actions=[gazebo_simulation]
        ),

        # 啟動導航
        TimerAction(
            period=12.0,
            actions=[bringup_launch]
        )
    ])
