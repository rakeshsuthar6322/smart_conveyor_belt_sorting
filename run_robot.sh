#!/bin/bash
set -e

echo "🤖 Booting XRbit Intelligent Sorting System..."

# 1. Activate the virtual environment
source .venv/bin/activate

# 2. Block the broken global packages
export PYTHONNOUSERSITE=1

# 3. PERMANENT FIX: Aggressively inject the .venv into ROS 2's brain
export PYTHONPATH=$PWD/.venv/lib/python3.12/site-packages:$PYTHONPATH

# 4. Source the ROS 2 compiled code
source install/setup.bash

# 5. Launch the system
ros2 launch xrbit_bringup system.launch.py
