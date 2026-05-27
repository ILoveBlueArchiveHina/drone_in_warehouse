import os

from launch import LaunchDescription


from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        # # 開啟 rviz
        Node(
                package='drone_in_warehouse',
                executable='py_minimal_publisher.py',
                name='oh_yeah',
                output='screen',
        ),
    ])