cmake_minimum_required(VERSION 3.8)
project(visualization_marker_tutorials)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(ament_cmake_ros REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rviz_common REQUIRED)
find_package(rviz_plugin_tutorial_msgs REQUIRED)

set(CMAKE_AUTOMOC ON)
qt6_wrap_cpp(MOC_FILES
  include/rviz_plugin_tutorial/point_display.hpp
)

add_library(point_display src/point_display.cpp ${MOC_FILES})
target_include_directories(point_display PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(point_display PUBLIC
  pluginlib::pluginlib
  rviz_common::rviz_common
  rviz_plugin_tutorial_msgs::rviz_plugin_tutorial_msgs
)
install(TARGETS point_display
        EXPORT export_rviz_plugin_tutorial
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
)
install(DIRECTORY include/
        DESTINATION include
)
install(FILES rviz_common_plugins.xml
        DESTINATION share/${PROJECT_NAME}
)
ament_export_include_directories(include)
ament_export_targets(export_rviz_plugin_tutorial)
pluginlib_export_plugin_description_file(rviz_common rviz_common_plugins.xml)

ament_export_dependencies(
  rclcpp
  geometry_msgs
  visualization_msgs)

add_executable(basic_shapes src/basic_shapes.cpp)
target_link_libraries(basic_shapes PUBLIC
  ${visualization_msgs_TARGETS}
  rclcpp::rclcpp
)

add_executable(points_and_lines src/points_and_lines.cpp)
target_link_libraries(points_and_lines PUBLIC
  ${geometry_msgs_TARGETS}
  ${visualization_msgs_TARGETS}
  rclcpp::rclcpp
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(TARGETS
  basic_shapes
  points_and_lines
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

ament_package()
