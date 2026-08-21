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

    # # WSL2 的 WSLg/D3D12 OpenGL driver 只支援到 GL 4.1，且缺少 GL_ARB_copy_image，
    # # Ogre2 建立材質產生 mipmap 時會呼叫 glCopyImageSubData(GL 4.3)，直接丟
    # # Ogre::UnimplementedException (GL3PlusTextureGpu::copyTo) 讓 ign gazebo 崩潰。
    # # 改用 Mesa llvmpipe 軟體渲染（GL 4.5，含 ARB_copy_image）繞開此限制。
    # # 若在有原生 GPU driver 的機器上執行，可用 use_software_gl:=false 關閉以取得較好效能。
    # declare_software_gl = DeclareLaunchArgument(
    #     'use_software_gl',
    #     default_value='true'
    # )
    # set_software_gl = SetEnvironmentVariable(
    #     'LIBGL_ALWAYS_SOFTWARE',
    #     PythonExpression(["'1' if '", LaunchConfiguration('use_software_gl'), "' == 'true' else '0'"])
    # )

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

    # 注意：LIBGL_ALWAYS_SOFTWARE 刻意放在 top-level（不要包進 scoped GroupAction），
    # 這樣同一個 ros2 launch 進程啟動的其他節點（RViz2 等）也會一起走 llvmpipe 軟體渲染。
    # 包進 scoped group 後，group 結束時環境會被還原，RViz 會改走 WSLg 的 D3D12
    # (Intel UHD 內顯) 硬體路徑，反而可能拖慢整個 WSLg 桌面合成。
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
        # declare_software_gl,
        # set_software_gl,
        declare_gui,
        gz_sim,
        bridge,
    ])