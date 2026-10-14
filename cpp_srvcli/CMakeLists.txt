cmake_minimum_required(VERSION 3.20)
project(cpp_srvcli)

#...

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tutorial_interfaces REQUIRED)         # CHANGE

add_executable(server src/add_two_ints_server.cpp)
target_link_libraries(server PUBLIC rclcpp::rclcpp tutorial_interfaces::tutorial_interfaces)  # CHANGE

add_executable(client src/add_two_ints_client.cpp)
target_link_libraries(client PUBLIC rclcpp::rclcpp tutorial_interfaces::tutorial_interfaces)  # CHANGE

install(TARGETS
  server
  client
  DESTINATION lib/${PROJECT_NAME})

ament_package()