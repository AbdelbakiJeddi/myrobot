cmake_minimum_required(VERSION 3.8)
project(myrobot_control)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  ${PROJECT_NAME}/go_to_goal_server.py
  ${PROJECT_NAME}/go_to_goal_client.py
  ${PROJECT_NAME}/twist_relay.py
  ${PROJECT_NAME}/simple_navigator.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
