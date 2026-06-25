# Gazebo Simulation

> **Active branch:** `feature/gazebo-simulation`

Gazebo simulation environment for the custom mobile robot — worlds, robot model, sensor plugins, and launch files used to validate navigation and behavior before deploying to the real hardware.

## Branches
- **`main`** — Stable integration branch.
- **`feature/real/nav2`** — Real-robot Nav2 implementation.
- **`feature/sim/simple_nav`** — Simple-navigation work in simulation.
- **`feature/real/simple_nav`** — Simple navigation on the real robot.

## What's on this branch

- `myrobot_description/` — URDF/xacro, robot state publisher, Gazebo launch and worlds (`empty.world`, `nav_test.world`).
- `myrobot_bringup/` — Launch files for simulated hardware interfaces (`simulated_robot.launch.py`).
- `myrobot_controller/` — ROS 2 controllers.
- `myrobot_firmware/` — Simulated low-level hardware interface (encoder-based).
- `myrobot_navigation/` — Simple navigation action and config; behavior trees.
- `myrobot_actions/` — Custom ROS 2 actions, services, and messages.

## Run

Build:
```bash
cd ~/simple_bot_ws
colcon build --symlink-install
source install/setup.bash
```

Launch Gazebo:
```bash
ros2 launch myrobot_description gazebo.launch.py            # empty world
ros2 launch myrobot_navigation navigation.launch.py        # world with waypoints
```

Visualize:
```bash
ros2 run rviz2 rviz2
```