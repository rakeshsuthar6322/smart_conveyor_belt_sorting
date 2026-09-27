# Start from the official ROS 2 Jazzy image
FROM ros:jazzy-ros-base

# 1. Install System Dependencies & C++ Build Tools
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ros-jazzy-cv-bridge \
    ros-jazzy-sensor-msgs \
    && rm -rf /var/lib/apt/lists/*

# 2. Create an isolated Python Virtual Environment inside the container
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --system-site-packages $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 3. Install our exact Python dependencies
RUN pip install --no-cache-dir "numpy<2.0.0" scipy ultralytics

# 4. Copy our ROS 2 Workspace into the container
WORKDIR /ros2_ws
COPY src/ ./src/

# 5. Build the C++ and Python nodes
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"

# 6. Setup the entrypoint
COPY docker/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# 7. Default command when container starts
CMD ["ros2", "launch", "xrbit_bringup", "system.launch.py"]
