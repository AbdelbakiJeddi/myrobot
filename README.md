# Real Robot — Simple Navigation

> **Active branch:** `feature/real/simple_nav`

Simple navigation stack for the physical robot (Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy). Implements a `Go_To_Pose` action server, a waypoint-following client, and an Arduino firmware PID with FeedForward.

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

## Run

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

## Recent changes
- Holding time between consecutive waypoint goals.
- Tuned rotate-to-heading PD gains.
- QoS updated for odometry subscribers.
- FeedForward added to the PID in the Arduino firmware.

## Known issues / next steps
- PID tuning on the real robot still to be refined (calibrate left/right feedforward independently).
- EKF relies on wheel-odometry yaw + gyro; consider adding a magnetometer for absolute heading.
- Full hardware-in-the-loop navigation test pending.