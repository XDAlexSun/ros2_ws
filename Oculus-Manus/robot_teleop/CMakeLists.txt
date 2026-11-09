cmake_minimum_required(VERSION 3.10)
project(robot_teleop)

# retargeting.hpp uses `inline const` variables, which need C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 1. Find packages first
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(type_description_interfaces REQUIRED)

# 2. Declare executable
add_executable(teleop_node src/teleop_node.cpp)
target_include_directories(teleop_node PRIVATE src)

# 3. Target dependencies (Pure CMake style)
target_link_libraries(teleop_node PRIVATE
  rclcpp::rclcpp
  std_msgs::std_msgs
  sensor_msgs::sensor_msgs
  sensor_msgs::sensor_msgs__rosidl_generator_cpp 
  std_srvs::std_srvs
  std_srvs::std_srvs__rosidl_generator_cpp
  type_description_interfaces::type_description_interfaces   
)

install(
  TARGETS teleop_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  # plain-assert math test, registered as a CTest so `colcon test` runs it
  add_executable(test_retargeting test/test_retargeting.cpp)
  target_include_directories(test_retargeting PRIVATE src) 
  add_test(NAME test_retargeting COMMAND test_retargeting)

  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
