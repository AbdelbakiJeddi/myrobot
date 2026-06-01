# Real Robot Hardware Workspace (Stable)

Welcome to the main branch of the `simple_bot` repository. This branch is strictly dedicated to running and testing on **real robot hardware**.

## Repository Organization

- **`main` branch (Current)**: Contains the codebase for deployment directly on the physical hardware.
- **`feature/gazebo-simulation` branch**: Contains the simulation logic to test navigation, computer vision, and strategy execution in Gazebo/Ignition before syncing changes to the real robot.
- **`feature/real/simple_nav` branch**: Development branch for implementing and testing simple navigation on real robot hardware.
- **`feature/sim/simple_nav` branch**: Development branch for implementing and testing simple navigation in simulation.
- **`old_feat/real/nav2` branch**: (Deprecated) Kept for historical reference.

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
- **`myrobot_navigation/`**: Simple Navigation action.
- **`myrobot_actions/`**: Custom ROS 2 action, service, and message definitions used across the ecosystem.

## Recent Advancements

The real hardware stack has reached several milestones:
1. **ROS 2 Control**: Successfully integrated standard `ros2_control` hardware interfaces to efficiently manage motor commands and read real-time encoder feedback.
2. **IMU Support**: Added active reading of the onboard Inertial Measurement Unit for heading corrections.
3. **EKF Filter**: Configured the `robot_localization` package to fuse wheel odometry and IMU data using an Extended Kalman Filter (EKF), achieving robust and high-frequency state estimation.
4. **custom Go To Goal navigation action**: with waypoints system.

## Known Issues
- [ ] Test the simple navigation stack on the real robot hardware.
- [ ] Start implementing computer vision modules (camera integration, object detection).
- [ ] Define and implement game strategy and behavior execution logic.

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Open a pull request to the `main` branch of this repository.
6. Ensure your pull request passes any automated checks and is reviewed by maintainers.

## License

This project is currently unlicensed. Please contact the maintainers for permission to use or distribute the code.