#!/usr/bin/env python3
"""前方安全时前进，发现障碍物时原地左转。"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float32


class SimpleCruiseNode(Node):
    def __init__(self) -> None:
        super().__init__('simple_cruise_node')
        # 接收处理后的单个距离值，输出巡航模式自己的速度话题。
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_cruise', 10)
        self.create_subscription(
            Float32, '/front_distance', self.distance_callback, 10
        )

        # 三个参数分别控制“多远开始避障”和“前进/转弯多快”。
        self.declare_parameter('safe_distance', 0.8)
        self.declare_parameter('forward_speed', 0.22)
        self.declare_parameter('turn_speed', 0.65)

    def distance_callback(self, msg: Float32) -> None:
        # 每次收到新距离都重新读取参数，支持课堂上动态修改。
        safe_distance = float(self.get_parameter('safe_distance').value)
        forward_speed = float(self.get_parameter('forward_speed').value)
        turn_speed = float(self.get_parameter('turn_speed').value)
        # 默认是全零速度；下面只根据距离选择“停止、转弯或前进”。
        cmd = Twist()

        if msg.data < 0.0:
            pass                         # 没有距离数据，保持停止
        elif msg.data < safe_distance:
            cmd.angular.z = turn_speed    # 有障碍物，原地左转
        else:
            cmd.linear.x = forward_speed  # 前方安全，向前行驶

        self.cmd_pub.publish(cmd)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SimpleCruiseNode()
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
