from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([      
        
        Node(
            package='drone_in_warehouse',
            executable='simple_control.py'
        ),
        
        # ArUco多標記識別節點
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard'
        )

    ])
