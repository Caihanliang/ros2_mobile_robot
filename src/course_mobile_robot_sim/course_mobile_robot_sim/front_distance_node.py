#!/usr/bin/env python3
"""从激光雷达数据中计算机器人正前方的最近距离。"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class FrontDistanceNode(Node):
    def __init__(self) -> None:
        super().__init__('front_distance_node')
        self.distance_pub = self.create_publisher(Float32, '/front_distance', 10)
        # Gazebo 雷达按传感器方式发送数据，本课直接使用推荐配置，不展开 QoS。
        self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data
        )

    def scan_callback(self, msg: LaserScan) -> None:
        valid_distances = []
        # 机器人正前方左右各取 30°，合起来是 60° 扇区。
        half_angle = math.radians(30.0)

        for index, distance in enumerate(msg.ranges):
            # LaserScan 只给出距离数组，需要根据下标计算每束激光的角度。
            angle = msg.angle_min + index * msg.angle_increment
            # 同时过滤扇区外、inf/nan 和雷达量程外的数据。
            if (
                abs(angle) <= half_angle
                and math.isfinite(distance)
                and msg.range_min <= distance <= msg.range_max
            ):
                valid_distances.append(distance)

        output = Float32()
        # 发布扇区内最近距离；-1.0 表示当前没有有效数据。
        output.data = min(valid_distances) if valid_distances else -1.0
        self.distance_pub.publish(output)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FrontDistanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
