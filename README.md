# Real Robot Navigation Development

Welcome to the `feature/real/simple_nav` branch of the `simple_bot` repository. This branch contains work in progress for integrating a simple navigation stack onto the real robot hardware. It is used for testing and refinement before merging to the `main` branch.

## Repository Organization

- **`main` branch**: Contains the stable, tested code for deployment on the physical hardware.
- **`feature/real/simple_nav` branch (Current)**: Development branch for implementing and testing simple navigation on real robot hardware.
- **`feature/gazebo-simulation` branch**: Contains the simulation logic to test navigation, computer vision, and strategy execution in Gazebo/Ignition before syncing changes to the real robot.
- **`feature/sim/simple_nav` branch**: Development branch for implementing and testing simple navigation in simulation.
- **`old_feat/real/nav2` branch**: (Deprecated) Kept for historical reference.

## Hardware Setup

The physical robot is powered by:
- **Compute**: Raspberry Pi 5 (8GB RAM)
- **OS**: Ubuntu Server 24.04
- **ROS Framework**: ROS 2 Jazzy

## Getting Started

Prerequisites:
- ROS 2 Jazzy
- Ubuntu 22.04/24.04
- Raspberry Pi 5 (or compatible hardware)

Build:
```
source /opt/ros/jazzy/setup.bash
colcon build
```

Run the simple navigation stack:
```
source install/setup.bash
ros2 launch myrobot_navigation go_to_goal.launch.py
```

## General Description

This repository provides the core ROS 2 workspace (`simple_bot_ws`) needed to operate the custom mobile robot. It manages hardware I/O, kinematic control, robust pose estimation, and autonomous navigation.

## Package Structure

- **`myrobot_description/`**: Contains the URDF, xacro files, and robot state publisher launch setups.
- **`myrobot_bringup/`**: Launch files for executing the real robot's core components and bringing up the hardware interfaces.
- **`myrobot_controller/`**: High-level ROS 2 controllers, multiplexers, and logic files.
- **`myrobot_firmware/`**: Low-level hardware interface layers and micro-controller connection logic.
- **`myrobot_navigation/`**: Simple Navigation action (in development).
- **`myrobot_actions/`**: Custom ROS 2 action, service, and message definitions used across the ecosystem.

## Recent Advancements

The real hardware stack in this branch has seen the following progress:
- Simple navigation action server implemented.
- Waypoint following functionality added.
- FeedForward term added to the PID in the Arduino firmware for improved motor control.
- Basic obstacle avoidance using sensor data.

## Known Issues
- [ ] Test the simple navigation stack on the real robot hardware under various conditions.
- [ ] Refine the PID tuning for different surfaces and loads.
- [ ] Integrate with computer vision modules for dynamic obstacle detection.
- [ ] Define and implement game strategy and behavior execution logic.

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix (based on this branch).
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Open a pull request to the `feature/real/simple_nav` branch of this repository.
6. Ensure your pull request passes any automated checks and is reviewed by maintainers.
7. Once approved, maintainers will merge into this branch and later into `main` after testing.

## License

This project is currently unlicensed. Please contact the maintainers for permission to use or distribute the code.