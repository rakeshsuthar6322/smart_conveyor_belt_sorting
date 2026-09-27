cmake_minimum_required(VERSION 3.8)
project(xrbit_motion)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(xrbit_msgs REQUIRED)

include_directories(include)

add_executable(motion_node src/motion_node.cpp)
ament_target_dependencies(motion_node rclcpp xrbit_msgs)

install(TARGETS motion_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_motion_protocol test/test_motion_protocol.cpp)
endif()

ament_package()
