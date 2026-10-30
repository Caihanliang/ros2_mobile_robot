#!/usr/bin/env python3
"""接收 RViz 目标点，控制机器人转向并直线前进。"""

import math
import time

import rclpy
from geometry_msgs.msg import PointStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float32, String


def normalize_angle(angle: float) -> float:
    """把角度限制到 -pi 至 pi。"""
    return math.atan2(math.sin(angle), math.cos(angle))


class SimpleGoalNavigationNode(Node):
    def __init__(self) -> None:
        super().__init__('simple_goal_navigation_node')

        # 保存机器人当前位姿、前方距离和最新目标点。
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.front_distance = -1.0
        self.last_distance_time = None
        self.goal_x = 0.0
        self.goal_y = 0.0
        self.has_goal = False
        self.mode = ''

        # 目标来自 RViz，当前位置来自里程计，障碍距离来自雷达处理节点。
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel_navigation', 10)
        self.create_subscription(PointStamped, '/clicked_point', self.goal_callback, 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(Float32, '/front_distance', self.distance_callback, 10)
        self.create_subscription(String, '/control_mode', self.mode_callback, 10)

        self.declare_parameter('goal_tolerance', 0.15)
        self.declare_parameter('obstacle_distance', 0.55)
        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.6)

    def goal_callback(self, msg: PointStamped) -> None:
        # 非导航模式不保存目标，防止之后切回导航时突然开始运动。
        if self.mode != 'NAVIGATION':
            self.get_logger().warn('请先切换到 NAVIGATION 模式。')
            return

        # 本节点使用 odom 中的机器人位置，因此目标点也必须属于 odom 坐标系。
        if msg.header.frame_id.lstrip('/') != 'odom':
            self.get_logger().warn('目标点不是 odom 坐标，请将 RViz Fixed Frame 改为 odom。')
            return

        self.goal_x = msg.point.x
        self.goal_y = msg.point.y
        self.has_goal = True
        self.get_logger().info(
            f'收到目标点：x={self.goal_x:.2f}, y={self.goal_y:.2f}'
        )

    def distance_callback(self, msg: Float32) -> None:
        self.front_distance = msg.data
        self.last_distance_time = time.monotonic()

    def mode_callback(self, msg: String) -> None:
        self.mode = msg.data
        # 离开导航模式时取消目标，并立即发布停车指令。
        if self.mode != 'NAVIGATION':
            self.has_goal = False
            self.cmd_pub.publish(Twist())

    def odom_callback(self, msg: Odometry) -> None:
        pose = msg.pose.pose
        self.x = pose.position.x
        self.y = pose.position.y

        # 里程计姿态是四元数，这里只换算移动机器人需要的 yaw 角。
        q = pose.orientation
        sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
        cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(sin_yaw, cos_yaw)

        # 每次收到新里程计都重新计算控制量，形成简单的位置闭环。
        if self.has_goal:
            self.move_to_goal()

    def move_to_goal(self) -> None:
        # 重新读取参数，使 ros2 param set 修改后立即生效。
        goal_tolerance = float(self.get_parameter('goal_tolerance').value)
        obstacle_distance = float(self.get_parameter('obstacle_distance').value)
        forward_speed = float(self.get_parameter('forward_speed').value)
        turn_speed = float(self.get_parameter('turn_speed').value)
        dx = self.goal_x - self.x
        dy = self.goal_y - self.y
        distance = math.hypot(dx, dy)
        target_yaw = math.atan2(dy, dx)
        yaw_error = normalize_angle(target_yaw - self.yaw)
        cmd = Twist()

        # 雷达距离超过 0.5 秒没有更新，就把它视为无效数据并保持停车。
        distance_data_valid = (
            self.last_distance_time is not None
            and time.monotonic() - self.last_distance_time <= 0.5
            and self.front_distance >= 0.0
        )

        # 控制顺序：到达则停；雷达无效或前方有障碍也停；安全时才转向或前进。
        if distance < goal_tolerance:
            self.has_goal = False
            self.get_logger().info('已到达目标点。')
        elif not distance_data_valid or self.front_distance < obstacle_distance:
            pass
        elif abs(yaw_error) > math.radians(15.0):
            cmd.angular.z = turn_speed if yaw_error > 0.0 else -turn_speed
        else:
            cmd.linear.x = forward_speed
            cmd.angular.z = yaw_error

        self.cmd_pub.publish(cmd)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SimpleGoalNavigationNode()
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
