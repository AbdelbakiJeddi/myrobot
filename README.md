# Real Robot Hardware Workspace

Welcome to the main branch of the `simple_bot` repository. This branch is strictly dedicated to running and testing on **real robot hardware**.

## Repository Organization

- **`main` branch (Current)**: Contains the codebase for deployment directly on the physical hardware.
- **`feature/gazebo-simulation` branch**: Contains the simulation logic to test navigation, computer vision, and strategy execution in Gazebo/Ignition before syncing changes to the real robot.

## Hardware Setup

The physical robot is powered by:
- **Compute**: Raspberry Pi 5 (8GB RAM)
- **OS**: Ubuntu Server 24.04
- **ROS Framework**: ROS 2 Jazzy

## General Description

This repository provides the core ROS 2 workspace (`simple_bot_ws`) needed to operate the custom mobile robot. It manages hardware I/O, kinematic control, robust pose estimation, and autonomous navigation.

## Package Structure

- **`myrobot_description/`**: Contains the URDF, xacro files, and robot state publisher launch setups.
- **`myrobot_bringup/`**: Launch files for executing the real robot's core components and bringing up the hardware interfaces.
- **`myrobot_controller/`**: High-level ROS 2 controllers, multiplexers, and logic files.
- **`myrobot_firmware/`**: Low-level hardware interface layers and micro-controller connection logic.
- **`myrobot_navigation/`**: Nav2 configurations, behavior trees, map files, and parameter definitions.
- **`myrobot_actions/`**: Custom ROS 2 action, service, and message definitions used across the ecosystem.

## Recent Advancements

The real hardware stack has reached several milestones:
1. **ROS 2 Control**: Successfully integrated standard `ros2_control` hardware interfaces to efficiently manage motor commands and read real-time encoder feedback.
2. **IMU Support**: Added active reading of the onboard Inertial Measurement Unit for heading corrections.
3. **EKF Filter**: Configured the `robot_localization` package to fuse wheel odometry and IMU data using an Extended Kalman Filter (EKF), achieving robust and high-frequency state estimation.
4. **Nav2 Integration**: Fully integrated with the current ROS 2 Navigation stack (Nav2) for dynamic path planning, obstacle avoidance, and goal execution straight on the Pi.


## Next Work / TODO List
- [ ] Test the simple navigation stack on the real robot hardware.
- [ ] Start implementing computer vision modules (camera integration, object detection).
- [ ] Define and implement game strategy and behavior execution logic.
