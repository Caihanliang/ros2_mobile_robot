#!/usr/bin/env python3
"""从手动、巡航和导航三路速度中选择一路。"""

import rclpy
from my_robot_interfaces.srv import SetControlMode
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import String


class ControlModeNode(Node):
    def __init__(self) -> None:
        super().__init__('control_mode_node')

        self.declare_parameter('initial_mode', 'MANUAL')
        self.mode = str(self.get_parameter('initial_mode').value).upper()
        # 参数写错时回到手动模式，避免意外转发自动控制指令。
        if self.mode not in ('MANUAL', 'CRUISE', 'NAVIGATION'):
            self.mode = 'MANUAL'

        # 三路速度最终都从同一个出口发往安全节点。
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_input', 10)
        self.mode_pub = self.create_publisher(String, '/control_mode', 10)

        # 三个控制节点可以同时运行，仲裁节点只转发当前模式的一路。
        self.create_subscription(
            Twist, '/cmd_vel_manual', self.manual_callback, 10
        )
        self.create_subscription(
            Twist, '/cmd_vel_cruise', self.cruise_callback, 10
        )
        self.create_subscription(
            Twist, '/cmd_vel_navigation', self.navigation_callback, 10
        )

        # 一个服务通过请求中的 mode 字段切换三种模式。
        self.create_service(
            SetControlMode, '/set_control_mode', self.set_mode_callback
        )
        # 周期发布模式，让稍晚启动的导航节点也能获知当前模式。
        self.create_timer(1.0, self.publish_mode)

        self.publish_mode()
        self.get_logger().info(f'当前控制模式：{self.mode}')

    def manual_callback(self, msg: Twist) -> None:
        if self.mode == 'MANUAL':
            self.cmd_pub.publish(msg)

    def cruise_callback(self, msg: Twist) -> None:
        if self.mode == 'CRUISE':
            self.cmd_pub.publish(msg)

    def navigation_callback(self, msg: Twist) -> None:
        if self.mode == 'NAVIGATION':
            self.cmd_pub.publish(msg)

    def set_mode_callback(self, request, response):
        new_mode = request.mode.upper()
        if new_mode not in ('MANUAL', 'CRUISE', 'NAVIGATION'):
            response.success = False
            response.message = '模式必须是 MANUAL、CRUISE 或 NAVIGATION。'
            return response

        # 切换速度来源前先发一条零速度，避免沿用上一模式的指令。
        self.cmd_pub.publish(Twist())
        self.mode = new_mode
        self.publish_mode()
        self.get_logger().info(f'已切换到 {self.mode} 模式')
        response.success = True
        response.message = f'已切换到 {self.mode} 模式。'
        return response

    def publish_mode(self) -> None:
        msg = String()
        msg.data = self.mode
        self.mode_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ControlModeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
