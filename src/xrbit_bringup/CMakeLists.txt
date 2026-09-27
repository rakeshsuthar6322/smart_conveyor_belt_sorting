cmake_minimum_required(VERSION 3.8)
project(xrbit_bringup)

find_package(ament_cmake REQUIRED)

# Install the launch and config directories so ROS can find them
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
