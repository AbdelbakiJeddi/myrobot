# Task: Draw the Full ROS 2 Topic Graph

## Description
The team has nodes that publish and subscribe across many topics. New teammates don't know what talks to what. Draw a single mermaid graph showing every topic the real-robot launch file wires up, who publishes, who subscribes. Use this as a learning tool: read each node's publishers and subscribers, list them in one place.

## Desired Output
- New file `tasks/onboarding/topic_graph.md` with:
  - One mermaid `graph LR` (or `flowchart LR`) showing nodes as boxes and topics as labels on the arrows.
  - Topics to include at minimum: `/cmd_vel`, `/myrobot_controller/cmd_vel`, `/joint_states`, `/odom`, `/odometry/filtered`, `/imu/out`, `/myrobot_controller/odom`, `navigate_to_pose` (action).
  - Nodes to include: `twist_relay`, `go_to_goal_server`, `go_to_goal_client`, `mpu6050_driver`, `ekf_filter_node`, `controller_manager`, `joint_state_broadcaster`, `myrobot_controller`, `robot_state_publisher`, `odom_logger`, `wheel_odometry_logger`.

## Input
- `src/myrobot_bringup/launch/real_robot.launch.py` (orchestration).
- Each node file under `src/` for its declared pub/sub.
- `src/myrobot_localization/config/ekf.yaml` (input / output topics).

## Configuration
- No code change. Read-only task with a doc deliverable.

## Docs Needed
- [ ] `tasks/onboarding/topic_graph.md`.
