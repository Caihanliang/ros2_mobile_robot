#!/usr/bin/env python3
"""读取键盘按键并发布手动速度。"""

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP_TEXT = """
键盘控制
----------------
w：前进    s：后退
a：左转    d：右转
k：停止    q：加速    e：减速
空格：停止    Ctrl+C：退出
"""


class KeyboardTeleopNode(Node):
    def __init__(self) -> None:
        super().__init__('keyboard_teleop_node')
        # 手动速度先发给模式切换节点，不直接控制底盘。
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_manual', 10)

        self.linear_speed = 0.25
        self.angular_speed = 0.7

    def handle_key(self, key: str) -> bool:
        if key == '\x03':
            return False

        # q 和 e 同时调整前进速度与转弯速度，每次变化 10%。
        if key == 'q':
            self.linear_speed *= 1.1
            self.angular_speed *= 1.1
            self.show_speed()
            return True
        if key == 'e':
            self.linear_speed *= 0.9
            self.angular_speed *= 0.9
            self.show_speed()
            return True

        # Twist 默认值全为 0，因此 k 和空格会发布停车指令。
        cmd = Twist()
        if key == 'w':
            cmd.linear.x = self.linear_speed
        elif key == 's':
            cmd.linear.x = -self.linear_speed
        elif key == 'a':
            cmd.angular.z = self.angular_speed
        elif key == 'd':
            cmd.angular.z = -self.angular_speed
        elif key not in ('k', ' '):
            return True

        self.cmd_pub.publish(cmd)
        return True

    def show_speed(self) -> None:
        self.get_logger().info(
            f'当前速度：linear={self.linear_speed:.2f}, '
            f'angular={self.angular_speed:.2f}'
        )


def read_key():
    # 最多等待 0.1 秒，避免程序一直阻塞在键盘读取操作上。
    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
    return sys.stdin.read(1) if ready else None


def main(args=None) -> None:
    rclpy.init(args=args)
    node = KeyboardTeleopNode()

    if not sys.stdin.isatty():
        node.get_logger().error('请在可交互终端中运行键盘节点。')
        node.destroy_node()
        rclpy.shutdown()
        return

    old_settings = termios.tcgetattr(sys.stdin)
    print(HELP_TEXT)
    try:
        # raw 模式可以直接读取单个按键，不需要按回车。
        tty.setraw(sys.stdin.fileno())
        while rclpy.ok():
            key = read_key()
            if key is not None and not node.handle_key(key):
                break
    except KeyboardInterrupt:
        pass
    finally:
        # 无论如何退出，都先停车并恢复终端原来的输入设置。
        node.cmd_pub.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
