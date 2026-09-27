#!/bin/bash
set -e
# Load ROS 2 and our Workspace
source /opt/ros/jazzy/setup.bash
source /ros2_ws/install/setup.bash
exec "$@"
