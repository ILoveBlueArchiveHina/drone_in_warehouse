from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
import os
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    # 定義模型路徑
    moveit_dir = get_package_share_directory("moveit_drone_config")
    # pkg_rt = get_package_share_directory('drone_in_warehouse')  # 自己的 config_package

    # moveit_config = (
    #     MoveItConfigsBuilder("crazyflie", package_name="moveit_config")
    #     .robot_description(file_path="config/model.urdf.xacro")
    #     .robot_description_semantic(file_path="config/crazyflie.srdf")
    #     .trajectory_execution(file_path=None)  # ⬅️ 關閉 controllers
    #     .planning_scene_monitor(
    #         publish_robot_description=True,
    #         publish_robot_description_semantic=True,
    #         publish_planning_scene=False,  # ⬅️ 不要發布監控場景
    #     )
    #     .to_moveit_configs()
    # )

    rtabmap_dir = os.path.join( get_package_share_directory('rtabmap_launch'), 'launch') 

    robot_desc = os.path.join(moveit_dir, 'config', 'crazyflie.urdf.xacro')
    robot_srdf = os.path.join(moveit_dir, 'config', 'crazyflie.sdrf')

    rtab_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(rtabmap_dir, 'rtabmap.launch.py')),
        launch_arguments={
            'log_level': 'error',               # 日誌等級
            'args': '--delete_db_on_start',     # 可選參數，啟動時清除上次紀錄
            'use_sim_time': 'true',             # 使用模擬時間
            'approx_sync': 'true',              # 啟用近似同步 (允許不同頻率的資料)
            'stereo': 'false',                  # (關鍵參數)如果只有光達，則關閉立體視覺
            'depth': 'false',                   # (關鍵參數)如果只有光達，則關閉深度影像
            'visual_odometry': 'false',         # 關閉視覺里程計
            'subscribe_scan': 'false',          # 關閉訂閱雷射掃描(2D)
            'subscribe_scan_cloud': 'true',     # 訂閱光達點雲(3D)
            'scan_cloud_topic': '/points',      # 修改為你的光達點雲主題
            'rtabmap_viz': 'false',             # 關閉 RTAB-Map 視覺化介面(可選)
            'frame_id': 'crazyflie/base_footprint',     # 修改為你的機器人基座框架ID
            'odom_frame_id': 'crazyflie/odom',          # 修改為你的里程計框架ID
            'publish_tf': 'true',               # 發佈 TF 資訊(map -> odom)
            'subscribe_imu': 'true',            # 訂閱 IMU 資料
            'imu_topic': '/imu',                # 修改為你的 IMU 主題
            'odom_topic': '/crazyflie/odom',    # 修改為你的里程計主題
            # 'icp_odometry': 'true',             # ICP 里程計
        }.items()
    )
    
    move_group_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(moveit_dir, 'launch', 'move_group.launch.py')),
        launch_arguments={
            'use_sim_time': 'true',             # 使用模擬時間
            "fake_execution": 'false',
            "allow_trajectory_execution": 'False',
            "moveit_manage_controllers": 'False',
        }.items()
    )




    return LaunchDescription([
        rtab_launch,
        move_group_launch,

        # Node(
        #     package='moveit_ros_move_group',
        #     executable='move_group',
        #     output='screen',
        #     parameters=[
        #         # robot description / srdf  (通常由 moveit_setup_assistant 產生, 這裡範例路徑)
        #         str(robot_desc),
        #         str(robot_srdf),
        #         # 關鍵：關閉執行功能 (plan-only)
        #         {'allow_trajectory_execution': 'False'},
        #         {'fake_execution': 'false'},
        #         # octomap / perception 參數（可視情況加入）
        #         {'octomap_frame': 'map'}
        #     ]
        # ),

        # Node(
        #     package="rviz2",
        #     executable="rviz2",
        #     name="rviz2",
        #     output="screen",
        #     arguments=["-d", moveit_dir + "/config/moveit.rviz"]
        # ),
        

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_lidar',
            output='screen',
            arguments=[
                '--x', '0.0',
                '--y', '0.0',
                '--z', '0.02',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'crazyflie/base_footprint',
                '--child-frame-id', 'crazyflie/base_footprint/multiranger']
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_imu',
            output='screen',
            arguments=[
                '--x', '0.0',
                '--y', '0.0',
                '--z', '0.02',
                '--roll', '0.0',
                '--pitch', '0.0',
                '--yaw', '0.0',
                '--frame-id', 'crazyflie/base_footprint',
                '--child-frame-id', 'crazyflie/base_footprint/imu']
        ),
    ])
