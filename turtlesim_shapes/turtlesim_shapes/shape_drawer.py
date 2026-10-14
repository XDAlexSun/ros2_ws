#!/usr/bin/env python3

import rclpy
import time
import math

from rclpy.node import Node
from geometry_msgs.msg import Twist

class ShapeDrawer(Node):
    def __init__(self):
        super().__init__('shape_drawer')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        time.sleep(1.0)  # Wait for subscriber connection

    def drive(self, linear_vel: float, angular_vel: float, duration: float):
        msg = Twist()
        msg.linear.x = float(linear_vel)
        msg.angular.z = float(angular_vel)
        
        start_time = time.time()
        while (time.time() - start_time) < duration:
            self.publisher_.publish(msg)
            time.sleep(0.05)
            
        # Stop motion after duration
        self.publisher_.publish(Twist())
        time.sleep(0.5)

    def draw_Tri(self, a: float, b: float, c: float, speed: float = 1.0):
        # Law of Cosines
        angle_A = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
        angle_C = math.acos((a**2 + b**2 - c**2) / (2 * a * b))

        turn1 = math.pi - angle_C
        turn2 = math.pi - angle_A
        turn_speed = 1.0

        # Side A
        self.drive(speed, 0.0, a / speed)
        self.drive(0.0, turn_speed, turn1 / turn_speed)

        # Side B
        self.drive(speed, 0.0, b / speed)
        self.drive(0.0, turn_speed, turn2 / turn_speed)

        # Side C
        self.drive(speed, 0.0, c / speed)

    def draw_Circ(self, radius: float, turns: float, speed: float = 1.0):
        # Angular velocity: w = v / r
        angular_vel = speed / radius
        # Time to complete all full circles
        total_time = (turns * 2.0 * math.pi) / angular_vel
        
        self.drive(linear_vel=speed, angular_vel=angular_vel, duration=total_time)

    def draw_Rect(self, length: float, height: float, speed: float = 1.0):
        turn_speed = 1.0
        turn_duration = (math.pi / 2.0) / turn_speed
        
        for _ in range(2):
            self.drive(speed, 0.0, length / speed)
            self.drive(0.0, turn_speed, turn_duration)
            self.drive(speed, 0.0, height / speed)
            self.drive(0.0, turn_speed, turn_duration)


def get_Shape():
    return input("Enter shape ('triangle', 'circle', 'rectangle'): ").strip().lower()

def get_input(shape: str):
    match shape.lower():
        case "triangle":
            while True:
                a = float(input("Length of side a: "))
                b = float(input("Length of side b: "))
                c = float(input("Length of side c: "))
                if a + b > c and b + c > a and a + c > b:
                    return a, b, c
                print("Invalid side lengths for a triangle! Try again.\n")

        case "circle":
            radius = float(input("Radius: "))
            turns = float(input("How many turns? "))
            return radius, turns

        case "rectangle":
            length = float(input("Length: "))
            height = float(input("Height: "))
            return length, height   


def main():
    rclpy.init()
    node = ShapeDrawer()

    try:
        while rclpy.ok():
            shape = get_Shape()
            if shape == "triangle":
                a, b, c = get_input(shape)
                node.draw_Tri(a, b, c)
            elif shape == "circle":
                radius, turns = get_input(shape)
                node.draw_Circ(radius, turns)
            elif shape == "rectangle":
                length, height = get_input(shape)
                node.draw_Rect(length, height)

            if input("\nDraw another shape? (yes/no): ").strip().lower() != 'yes':
                break
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()