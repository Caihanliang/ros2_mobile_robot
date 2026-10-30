# 搭建移动机器人仿真

## 现成基础设施

- 组件化单一模型：顶层 Xacro 负责装配，`urdf/components/` 分别维护结构、物理属性和 Gazebo 插件
- `ros_gz_sim`：从 `robot_description` 生成实体，并在内部完成 URDF→SDF
- Gazebo：物理世界与传感器仿真
- DiffDrive 插件：接收 `/cmd_vel` 并产生运动和里程计
- JointStatePublisher 插件：发布真实车轮关节状态
- `ros_gz_bridge`：Gazebo 与 ROS 2 消息桥接
- `robot_state_publisher`：根据同一 URDF 和 `/joint_states` 发布机器人 TF
- RViz：数据可视化

## 统一坐标系

```text
odom → base_footprint → base_link → lidar_support_link → lidar_link
```

可选 SLAM 扩展启动后，坐标链前面会增加 `map → odom`。

- `base_footprint`：机器人在地面的投影，供里程计和简易导航使用；
- `base_link`：车体几何中心，相对地面高度 0.16 m；
- 两个驱动轮和万向轮最低点同在 `Z=0`；
- 雷达支撑杆拥有 visual、collision 与 inertial，雷达不再悬空。

## 自己编写的节点

### keyboard_teleop_node.py

```text
键盘输入 → Twist → /cmd_vel_manual
```

`w/s` 控制前进和后退，`a/d` 控制左右转，`q/e` 每次把线速度和角速度提高或降低 10%；最终速度仍受安全节点的最大速度参数限制。

### control_mode_node.py

```text
/cmd_vel_manual + /cmd_vel_cruise + /cmd_vel_navigation
  → 模式选择、切换时停车 → /cmd_vel_input
```

`/set_control_mode` 使用自定义 `SetControlMode.srv`，请求中的 `mode` 可以是 `MANUAL`、`CRUISE` 或 `NAVIGATION`。

### cmd_vel_safety_node.py

```text
/cmd_vel_input → 限速、超时停车 → /cmd_vel
```

### front_distance_node.py

```text
/scan → 取正前方 50° 范围内的最近距离 → /front_distance
```

重点：Publisher、Subscriber、Service、Parameter、消息加工和节点解耦。安全节点用三个常见参数演示“声明参数 → YAML 赋值 → 节点读取”：最大线速度、最大角速度和指令超时时间。

## 可选扩展

`slam.launch.py` 使用 `/scan`、`/odom` 和 TF 建图。该部分建议只做结果演示，不逐项介绍 `slam_toolbox.yaml`；建图时把 RViz 的 Fixed Frame 改为 `map`，主线实验仍使用 `odom`。
