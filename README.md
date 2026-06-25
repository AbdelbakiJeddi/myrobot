# Real Robot — Simple Navigation

> **Active branch:** `feature/real/simple_nav`

Simple navigation stack for the physical robot (Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy). Implements a `Go_To_Pose` action server, a waypoint-following client, and an Arduino firmware PID with FeedForward.

## Branches
- **`main`** — Stable integration branch.
- **`feature/sim/nav2`** — Gazebo simulation of the same stack.
- **`feature/sim/simple_nav`** — Simple-navigation work in simulation.
- **`feature/real/nav2`** — Real-robot Nav2 implementation.

## What's on this branch

- `myrobot_description/` — URDF/xacro, robot state publisher, RViz display.
- `myrobot_bringup/` — Launch files for the real hardware (`real_robot.launch.py`).
- `myrobot_controller/` — ROS 2 controllers (`controller.launch.py`).
- `myrobot_firmware/` — Arduino firmware with FeedForward PID (encoder-based); hardware interface launch.
- `myrobot_navigation/` — `Go_To_Pose` action server + client, waypoint client (`go_to_goal_client.py`), odom logger, `waypoints.yaml`.
- `myrobot_actions/` — Custom ROS 2 actions, services, and messages.

## Run

Build:
```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

Launch the simple navigation stack:
```bash
ros2 launch myrobot_navigation go_to_goal.launch.py
```

## Recent changes
- Holding time between consecutive waypoint goals.
- Tuned rotate-to-heading PD gains.
- QoS updated for odometry subscribers.
- FeedForward added to the PID in the Arduino firmware.

## Known issues
- Waypoints system fails to execute the second and third goals.
- Full hardware-in-the-loop test pending.
- PID tuning on the real robot still to be refined.