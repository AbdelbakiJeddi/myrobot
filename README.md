# myrobot — Nav2 Stack (Simulation + Real)

> **Branch:** `feature/nav2` — unified Nav2 implementation running on the physical robot (Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy) and in Gazebo simulation.

## Branches
- **`main`** — Stable integration branch.
- **`feature/nav2`** — Unified Nav2 stack (this branch). Two bringup launch files: real hardware and Gazebo simulation.
- **`feature/sim/simple_nav`** — Simple-navigation work in simulation.
- **`feature/real/simple_nav`** — Simple navigation on the real robot.

## Package Structure

- **`myrobot_description/`** — URDF/xacro robot model, robot state publisher, Gazebo launch and worlds.
- **`myrobot_bringup/`** — Central bringup entry points (`real_robot.launch.py`, `simulated_robot.launch.py`).
- **`myrobot_controller/`** — ROS 2 controllers (diff-drive) bridging cmd_vel to the drivetrain.
- **`myrobot_firmware/`** — Low-level hardware interface (C++ ros2_control plugin) + IMU/MPU6050 driver + EKF config.
- **`myrobot_navigation/`** — Nav2 configs: planner, controller, costmaps, behavior trees, maps.
- **`myrobot_actions/`** — Custom ROS 2 actions, services, and messages.

## Run

Build:
```bash
cd ~/simple_bot_ws
colcon build
source install/setup.bash
```

### Real hardware
```bash
ros2 launch myrobot_bringup real_robot.launch.py
```

### Simulation
```bash
ros2 launch myrobot_bringup simulated_robot.launch.py
```

### Send a goal
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
    "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

You can also set goals interactively from RViz using the **Nav2 Goal** tool.
