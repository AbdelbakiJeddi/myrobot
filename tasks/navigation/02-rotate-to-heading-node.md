# Task: Rotate to Desired Heading Node (PID, YAML-configurable)

## Description
Implement a standalone ROS 2 node that rotates the robot to a target yaw. Subscribes to odom for current heading, publishes `cmd_vel` (angular z) via PID. Gains and tolerances loaded from a YAML file so the team can tune without recompiling.

The existing `go_to_goal_server.py` does this inline. Pull rotate out as its own reusable node so other behaviors (recovery, manual align) can call it.

## Desired Output
- New node `rotate_to_heading.py` in `src/myrobot_control/myrobot_control/`.
- New config file `src/myrobot_control/config/rotate_params.yaml` with: `kp`, `ki`, `kd`, `tolerance_rad`, `max_angular_vel`, `control_rate_hz`.
- Launch entry in `control.launch.py` to start the node (gated by a launch arg).
- Brief unit-style smoke test (or dry-run) showing PID does not oscillate on a synthetic odom feed.

## Input
- `src/myrobot_control/config/control_params.yaml` — current param style to follow.
- `nav_msgs/msg/Odometry` for current pose.
- `geometry_msgs/msg/Twist` for output.

## Configuration
- New file `src/myrobot_control/config/rotate_params.yaml`:
  ```yaml
  rotate_to_heading:
    ros__parameters:
      kp: 1.2
      ki: 0.0
      kd: 0.05
      tolerance_rad: 0.05
      max_angular_vel: 0.8
      control_rate_hz: 20.0
  ```
- Launch arg `enable_rotate_node:=true` (default `false` to keep current behavior).

## Docs Needed
- [ ] `src/myrobot_control/README.md` — node purpose, params, topic in/out.
- [ ] `TASK_DONE_TEMPLATE.md` filled with PID chosen, tolerance, test result.
- [ ] Tuning changes (if any) noted in PR body.
