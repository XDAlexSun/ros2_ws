#!/usr/bin/env python3

import rclpy
import time
import math

from rclpy.node import Node
from geometry_msgs.msg import Twist

class ShapeDrawer(Node):
    def __init__(self):
        super().__init__('circle')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.drawCircle) # Wait for subscriber connection

    def drawCircle(self):
        msg = Twist()
        msg.linear.x = 1.0 #change if necessary
        msg.angular.z = 1.0
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ShapeDrawer()
    try:
        rclpy.spin(node)
    except:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__== '__main__':
    main()