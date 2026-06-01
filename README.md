# Gazebo Simulation Development

Welcome to the `feature/gazebo-simulation` branch of the `simple_bot` repository. This branch contains the simulation worlds, models, and launch files for testing the robot in Gazebo/Ignition. It is used to validate algorithms and behaviors before deploying to real hardware.

## Repository Organization

- **`main` branch**: Contains the stable, tested code for deployment on the physical hardware.
- **`feature/real/simple_nav` branch**: Development branch for implementing and testing simple navigation on real robot hardware.
- **`feature/sim/simple_nav` branch**: Development branch for implementing and testing simple navigation in simulation.
- **`feature/gazebo-simulation` branch (Current)**: Development branch for setting up and testing Gazebo/Ignition simulation environments.
- **`old_feat/real/nav2` branch**: (Deprecated) Kept for historical reference.

## Hardware Setup

Note: This branch is for simulation. The simulated robot is modeled after the real robot hardware:
- **Compute**: Raspberry Pi 5 (8GB RAM) (simulated)
- **OS**: Ubuntu Server 24.04 (simulated)
- **ROS Framework**: ROS 2 (distro matching simulation, e.g., Humble or Iron)
- **Simulator**: Gazebo or Ignition (as specified in the launch files)

## General Description

This repository provides the core ROS 2 workspace (`simple_bot_ws`) for simulating the custom mobile robot in Gazebo/Ignition. It focuses on the simulation environment setup, including worlds, robot models, and sensor plugins, to enable testing of navigation algorithms and behaviors in a realistic virtual setting.

## Package Structure

- **`myrobot_description/`**: Contains the URDF, xacro files, and robot state publisher launch setups. Includes Gazebo-specific launch files (`gazebo.launch.py`) and Gazebo-specific URDF/xacro (`myrobot_gazebo.xacro`).
- **`myrobot_bringup/`**: Launch files for executing the robot's core components in simulation and bringing up the hardware interfaces.
- **`myrobot_controller/`**: High-level ROS 2 controllers, multiplexers, and logic files.
- **`myrobot_firmware/`**: Low-level hardware interface layers and micro-controller connection logic (simulated).
- **`myrobot_navigation/`**: Simple Navigation action (may be used in simulation).
- **`myrobot_actions/`**: Custom ROS 2 action, service, and message definitions used across the ecosystem.

## Recent Advancements

The Gazebo simulation setup in this branch has seen the following progress:
- Integration of Gazebo launch files and world files.
- Accurate robot model with Gazebo-specific plugins (e.g., for sensors, motor control).
- Creation of reusable simulation worlds for testing navigation and behaviors.

## Known Issues
- [ ] Verify the exact launch file and world file names for simulation.
- [ ] Test the simulation under various conditions to ensure fidelity.
- [ ] Refine the robot model for better physical interaction simulation.
- [ ] Integrate with computer vision modules for dynamic obstacle detection in Gazebo.
- [ ] Define and implement game strategy and behavior execution logic in Gazebo simulation.

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix (based on this branch).
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Open a pull request to the `feature/gazebo-simulation` branch of this repository.
6. Ensure your pull request passes any automated checks and is reviewed by maintainers.
7. Once approved, maintainers will merge into this branch and later into `main` after testing.

## License

This project is currently unlicensed. Please contact the maintainers for permission to use or distribute the code.