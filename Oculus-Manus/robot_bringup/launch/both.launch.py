"""RViz AND MuJoCo driven by ONE teleop node, so both hands move together.

  camera (or fake hand) -> teleop_node -> /joint_states -+-> robot_state_publisher -> RViz
                                                         +-> mujoco_hand_node      -> MuJoCo

  ros2 launch robot_bringup both.launch.py fake:=true   # synthetic hand, no camera
  ros2 launch robot_bringup both.launch.py              # real webcam

Run this INSTEAD of teleop.launch.py / sim.launch.py, never alongside them: each of those
starts its own vision and teleop nodes, which is why two windows opened separately look unconnected.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    urdf_file = os.path.join(
        get_package_share_directory('robot_description'), 'urdf', 'robot_hand.urdf')
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    fake = LaunchConfiguration('fake')

    return LaunchDescription([

        DeclareLaunchArgument('fake', default_value='false',
                              description='Use a synthetic hand instead of the webcam'),

        Node(package='robot_vision', executable='mediapipe_world_node',
             output='screen', condition=UnlessCondition(fake)),

        Node(package='robot_vision', executable='fake_hand_node',
             output='screen', condition=IfCondition(fake)),

        # one teleop node; its output goes to /joint_states, the topic RViz's
        # robot_state_publisher reads
        Node(package='robot_teleop', executable='teleop_node', output='screen',
             parameters=[{'output_topic': '/joint_states'}]),

        Node(package='robot_state_publisher', executable='robot_state_publisher',
             output='screen', parameters=[{'robot_description': robot_description}]),

        Node(package='rviz2', executable='rviz2', output='screen',
             arguments=['-d', os.path.join(
                 get_package_share_directory('robot_description'), 'rviz', 'robot_hand.rviz')]),

        # MuJoCo listens to the SAME topic. It reports what it actually did on
        # /hand/sim_joint_states, so it never writes to /joint_states and cannot fight RViz.
        Node(package='robot_sim', executable='mujoco_hand_node', output='screen',
             parameters=[{'command_topic': '/joint_states'}]),
    ])
