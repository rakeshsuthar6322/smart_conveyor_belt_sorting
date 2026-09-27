#!/bin/bash
# This script completely wipes the ROS environment variables to prevent Humble/Jazzy mixing
echo "Cleaning mixed ROS environment variables..."
unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH
unset ROS_DISTRO
unset ROS_VERSION
unset PYTHONPATH
unset LD_LIBRARY_PATH

echo "Sourcing Jazzy..."
source /opt/ros/jazzy/setup.bash

echo "Starting Build..."
colcon build
