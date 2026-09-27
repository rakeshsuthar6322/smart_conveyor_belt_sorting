#!/bin/bash
set -e

# Source ROS 2
source /opt/ros/jazzy/setup.bash
source /ros2_ws/install/setup.bash

# PERMANENT FIX for Docker: Prevent ROS 2 from wiping the venv path
export PYTHONPATH=/opt/venv/lib/python3.12/site-packages:$PYTHONPATH

# Execute the CMD from the Dockerfile
exec "$@"
