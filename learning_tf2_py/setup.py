import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'learning_tf2_py'
#   <launch>
    # <node
    #   pkg="tf2_ros" exec="static_transform_publisher"
    #   args="--x 0 --y 0 --z 1 --yaw 0 --pitch 0 --roll 0 --frame-id world --child-frame-id mystaticturtle"
    # />
#   </launch>
# 
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='alex',
    maintainer_email='alex@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'static_turtle_tf2_broadcaster = learning_tf2_py.static_turtle_tf2_broadcaster:main',
        ],
    },
)
# add_executable(static_turtle_tf2_broadcaster src/static_turtle_tf2_broadcaster.cpp)
# target_link_libraries(
#    static_turtle_tf2_broadcaster PUBLIC
#    geometry_msgs::geometry_msgs
#    rclcpp::rclcpp
#    tf2::tf2
#    tf2_ros::tf2_ros
# )
# add_executable(turtle_tf2_listener src/turtle_tf2_listener.cpp)
# target_link_libraries(
    # turtle_tf2_listener PUBLIC
    # geometry_msgs::geometry_msgs
    # rclcpp::rclcpp
    # tf2::tf2
    # tf2_ros::tf2_ros
    # turtlesim_msgs::turtlesim_msgs
# )