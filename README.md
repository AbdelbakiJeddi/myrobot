# Real Robot — Nav2 Implementation

This branch (`old_feat/real/nav2`) hosts the **real robot implementation** of the ROS 2 Navigation Stack (Nav2), running directly on the physical hardware (Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy). It complements `feature/gazebo-simulation` — logic is validated in Gazebo first, then ported and tuned here against the real drivetrain, IMU, and lidar.

## Package Structure

- **`myrobot_description/`** — URDF, xacro, and robot state publisher setups.
- **`myrobot_bringup/`** — Launch files for hardware interfaces and Nav2 bringup.
- **`myrobot_controller/`** — ROS 2 controllers bridging Nav2 commands to the drivetrain.
- **`myrobot_firmware/`** — Low-level hardware interface and micro-controller connection.
- **`myrobot_navigation/`** — Nav2 configs: planners, controllers, costmaps, behavior trees, maps, AMCL params.
- **`myrobot_actions/`** — Custom ROS 2 actions, services, and messages.

## How to Run

### 1. Build the workspace
```bash
cd ~/simple_bot_ws
colcon build 
source install/setup.bash
```

### 2. Bring up hardware + localization
```bash
ros2 launch myrobot_bringup real_robot.launch.py
```

### 3. Launch Nav2
```bash
ros2 launch myrobot_navigation navigation.launch.py
```

### 4. Send a goal
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
    "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

You can also set goals interactively from RViz using the **Nav2 Goal** tool.