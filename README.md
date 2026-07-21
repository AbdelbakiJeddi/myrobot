# Real Robot — Simple Navigation

> **Active branch:** `feature/real/simple_nav`

Simple navigation stack for the physical robot (Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy). Implements a `Go_To_Pose` action server, a waypoint-following client, and an Arduino firmware PID with FeedForward.

## General Description

This repository provides the core ROS 2 workspace needed to operate the custom mobile robot. It manages hardware I/O, kinematic control, robust pose estimation, and autonomous navigation.

The real hardware stack has reached several milestones:
1. **ROS 2 Control**: standard `ros2_control` hardware interfaces for motor commands and encoder feedback.
2. **IMU Support**: active MPU6050 reading for heading corrections.
3. **EKF Filter**: `robot_localization` fuses wheel odometry and IMU data.
4. **Go To Goal navigation action** with waypoints system.

## Branches
- **`main`** — Stable integration branch.
- **`feature/sim/nav2`** — Gazebo simulation of the same stack.
- **`feature/sim/simple_nav`** — Simple-navigation work in simulation.
- **`feature/real/nav2`** — Real-robot Nav2 implementation.

## Package Architecture

Single-responsibility ROS 2 packages under `src/`:

| Package | Responsibility |
|---|---|
| `myrobot_interfaces` | Custom actions/msgs/srvs (`NavigateToPose.action`) |
| `myrobot_description` | URDF/xacro robot model, RViz display |
| `myrobot_hardware` | ros2_control `SystemInterface` plugin (C++) + Arduino firmware (robot_control, feedforward) |
| `myrobot_localization` | MPU6050 IMU driver + robot_localization EKF config |
| `myrobot_control` | GoToGoal action server/client, twist_relay, simple_navigator |
| `myrobot_utils` | Diagnostics: odom_logger, path_visualizer, wheel_odometry_logger |
| `myrobot_bringup` | Central launch entry point + all configs, maps, waypoints |

## Getting Started

Prerequisites:
- ROS 2 Jazzy
- Ubuntu 22.04/24.04
- Raspberry Pi 5 (or compatible hardware)

Build:
```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

Launch the full real-robot stack (add `launch_navigation:=true` for nav):
```bash
ros2 launch myrobot_bringup real_robot.launch.py
```

Launch navigation only (requires hardware already running):
```bash
ros2 launch myrobot_control control.launch.py
```

## Contributing

Read `GENERAL_RULES.md` first. Summary:

1. Pick or create a ClickUp task. Use `NEW_TASK_TEMPLATE.md` for new ones.
2. Branch: `type/CU-id-kebab-slug`. Example: `feat/CU-abc123-goal-tolerance`.
3. Code, commit with Conventional Commits, reference `CU-abc123`.
4. Push branch, open PR. Title = commit subject.
5. Fill PR body from `TASK_DONE_TEMPLATE.md`.
6. Wait for 1+ approval and CI green.
7. Move task to `Done` only after merge + verified on rig/sim.

## Documenting Your Work

Two templates in repo root:

- **`NEW_TASK_TEMPLATE.md`** — copy at task creation. Fields: Description, Desired Output, Input, Configuration, Docs Needed.
- **`TASK_DONE_TEMPLATE.md`** — copy into PR body when done. Fields: Short Description, What Did, Data, Input, Output, Changes, Packages Needed, How to Run, Args.

Tuning changes (PID, EKF, gains): document old vs new value, why, and link the test run in the PR body. No silent retunes.

Full rules: see `GENERAL_RULES.md`.

## Recent changes
- Holding time between consecutive waypoint goals.
- Tuned rotate-to-heading PD gains.
- QoS updated for odometry subscribers.
- FeedForward added to the PID in the Arduino firmware.

## Known issues / next steps
- PID tuning on the real robot still to be refined (calibrate left/right feedforward independently).
- EKF relies on wheel-odometry yaw + gyro; consider adding a magnetometer for absolute heading.
- Full hardware-in-the-loop navigation test pending.
- Start implementing computer vision modules (camera integration, object detection).
- Define and implement game strategy and behavior execution logic.
