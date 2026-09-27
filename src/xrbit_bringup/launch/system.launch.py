import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('xrbit_bringup'), 'config', 'params.yaml'
    )

    return LaunchDescription([
        Node(package='xrbit_vision', executable='vision_node', name='vision_node', parameters=[config]),
        Node(package='xrbit_sorter', executable='sorter_node', name='sorter_node', parameters=[config]),
        Node(package='xrbit_motion', executable='motion_node', name='motion_node', parameters=[config]),
        
        # New Sensor Node added here!
        Node(
            package='xrbit_sensors',
            executable='sensor_node',
            name='sensor_node',
            parameters=[config]
        )
    ])
