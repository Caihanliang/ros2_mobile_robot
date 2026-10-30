#!/usr/bin/env python3
"""限制速度，并在速度指令中断时自动停车。"""

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


def clamp(value: float, limit: float) -> float:
    return max(-limit, min(value, limit))


class CmdVelSafetyNode(Node):
    def __init__(self) -> None:
        super().__init__('cmd_vel_safety_node')
        # 接收仲裁后的速度，检查后才发布到真正控制底盘的 /cmd_vel。
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Twist, '/cmd_vel_input', self.cmd_callback, 10)
        self.create_timer(0.1, self.check_timeout)

        # 只把最常调整的安全数值设计成参数。
        self.declare_parameter('max_linear_speed', 0.5)
        self.declare_parameter('max_angular_speed', 1.2)
        self.declare_parameter('command_timeout', 1.0)

        # 记录最后一条运动指令，用于判断上游节点是否已经中断。
        self.moving = False
        self.last_cmd_time = time.monotonic()

    def cmd_callback(self, msg: Twist) -> None:
        # 每次回调重新读取参数，使 ros2 param set 能立即生效。
        max_linear = float(self.get_parameter('max_linear_speed').value)
        max_angular = float(self.get_parameter('max_angular_speed').value)

        # 只转发本项目会使用的前后速度和转向速度，并限制最大值。
        cmd = Twist()
        cmd.linear.x = clamp(msg.linear.x, max_linear)
        cmd.angular.z = clamp(msg.angular.z, max_angular)
        self.cmd_pub.publish(cmd)

        self.last_cmd_time = time.monotonic()
        self.moving = cmd.linear.x != 0.0 or cmd.angular.z != 0.0

    def check_timeout(self) -> None:
        timeout = float(self.get_parameter('command_timeout').value)
        # 上游超过指定时间没有继续发布速度时，主动发送停车指令。
        if self.moving and time.monotonic() - self.last_cmd_time > timeout:
            self.stop()
            self.get_logger().info('速度指令超时，机器人自动停止。')

    def stop(self) -> None:
        # 发布一个全零 Twist 就表示停车。
        self.cmd_pub.publish(Twist())
        self.moving = False


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CmdVelSafetyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
