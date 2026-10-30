# 多节点通信应用开发

```text
Gazebo /scan
  ↓
front_distance_node
  ↓ /front_distance
simple_cruise_node
  ↓ /cmd_vel_cruise
control_mode_node
  ↓ /cmd_vel_input
cmd_vel_safety_node
  ↓ /cmd_vel
Gazebo DiffDrive
```

## 自编节点

- `simple_cruise_node.py`
  - 订阅 `/front_distance`
  - 用一个距离阈值判断前进或转弯
  - 发布 `/cmd_vel_cruise`
  - 参数：`safe_distance`、`forward_speed`、`turn_speed`

- `simple_goal_navigation_node.py`
  - 订阅 RViz `/clicked_point`、`/odom` 和 `/front_distance`
  - 只接收 `odom` 坐标系目标，先转向再直线前进，到达、遇障碍或雷达数据中断时停车
  - 发布 `/cmd_vel_navigation`
  - 参数：`goal_tolerance`、`obstacle_distance`、`forward_speed`、`turn_speed`

- `control_mode_node.py`
  - 在手动、巡航和导航三路速度之间进行选择
  - 提供一个 `/set_control_mode` 服务，请求字段决定切换到哪种模式
  - 只把当前模式的速度转发到 `/cmd_vel_input`

本节不再修改机器人几何模型；所有节点继续使用上一节同一套组件化 Xacro 所产生的 `/scan`、`/odom` 和 TF。简易导航是基于里程计的直线目标跟踪，不是 Nav2 路径规划；路径被障碍物挡住时会停车。

应用参数统一放在 `config/application_nodes.yaml`。只参数化速度和距离这类适合方便调整的数值，话题名和控制结构保持固定。
