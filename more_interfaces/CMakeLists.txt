cmake_minimum_required(VERSION 3.20)
project(more_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 1. Define and generate your interfaces FIRST
set(msg_files
  "msg/AddressBook.msg"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
)

# 2. Define your executable AFTER the interfaces are declared
add_executable(publish_address_book src/publish_address_book.cpp)
# ament_target_dependencies(publish_address_book rclcpp)

# 3. Force the executable to wait for the message headers to compile
rosidl_get_typesupport_target(cpp_typesupport_target "${PROJECT_NAME}" "rosidl_typesupport_cpp")
add_dependencies(publish_address_book "${cpp_typesupport_target}")

# 4. Install targets
install(TARGETS
    publish_address_book
  DESTINATION lib/${PROJECT_NAME})

# Export dependencies for downstream packages
ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Final package macro
ament_package()