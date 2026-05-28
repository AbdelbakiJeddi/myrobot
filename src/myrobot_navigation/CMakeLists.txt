cmake_minimum_required(VERSION 3.8)
project(myrobot_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch maps config
  DESTINATION share/${PROJECT_NAME}
)

# Install Python package
ament_python_install_package(${PROJECT_NAME})

# Install executable scripts
install(
  PROGRAMS ${PROJECT_NAME}/odom_logger.py
  PROGRAMS ${PROJECT_NAME}/go_to_pose_action.py
  PROGRAMS ${PROJECT_NAME}/go_to_pose_client.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
