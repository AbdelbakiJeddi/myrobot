cmake_minimum_required(VERSION 3.8)
project(myrobot_utils)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  ${PROJECT_NAME}/odom_logger.py
  ${PROJECT_NAME}/path_visualizer.py
  ${PROJECT_NAME}/wheel_odometry_logger.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
