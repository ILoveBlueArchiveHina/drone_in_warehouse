#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('drone_in_warehouse')
    
    # 啟動完整的 nav2 系統
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'rtab_slam3d.launch.py'))
    )
    
    # 啟動測試節點
    test_node = Node(
        package='drone_in_warehouse',
        executable='test_waypoint_action.py',
        name='waypoint_action_tester',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    return LaunchDescription([
        nav2_launch,
        test_node
    ])
