#!/usr/bin/env python3

import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareDrawer(Node):
    def __init__(self):
        super().__init__('square_drawer')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        
        # States: 'MOVE', 'PAUSE', 'TURN', 'FINISHED'
        self.state = 'MOVE'
        self.next_state = 'TURN'
        
        # Parameters
        self.linear_speed = 0.2     # units/sec
        self.side_length = 2.0      # units
        self.angular_speed = 0.2    # rad/sec
        self.turn_angle = math.pi / 2.0  # 90 degrees
        self.pause_duration = 0.5   # 0.5s pause between moves to kill momentum

        # Durations
        self.move_duration = self.side_length / self.linear_speed
        self.turn_duration = self.turn_angle / self.angular_speed
        
        self.sides_completed = 0
        self.start_time = self.get_clock().now()
        
        # High frequency loop (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop)

    def control_loop(self):
        msg = Twist()
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9

        if self.state == 'FINISHED':
            # Publish 0 velocity to stay stopped
            self.publisher_.publish(Twist())
            return

        elif self.state == 'MOVE':
            if elapsed < self.move_duration:
                msg.linear.x = self.linear_speed
            else:
                # Force zero velocity and enter brief pause
                self.publisher_.publish(Twist())
                self.state = 'PAUSE'
                self.next_state = 'TURN'
                self.start_time = now
                return

        elif self.state == 'TURN':
            if elapsed < self.turn_duration:
                msg.angular.z = self.angular_speed
            else:
                # Force zero velocity and enter brief pause
                self.publisher_.publish(Twist())
                self.sides_completed += 1
                
                if self.sides_completed >= 4:
                    self.state = 'FINISHED'
                else:
                    self.state = 'PAUSE'
                    self.next_state = 'MOVE'
                
                self.start_time = now
                return

        elif self.state == 'PAUSE':
            # Hold stationary to let physics/timer settle
            if elapsed >= self.pause_duration:
                self.state = self.next_state
                self.start_time = now

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDrawer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()