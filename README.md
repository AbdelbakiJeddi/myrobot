# Simulated Robot Navigation Development

Welcome to the `feature/sim/simple_nav` branch of the `simple_bot` repository. This branch contains work in progress for integrating a simple navigation stack in simulation. It is used for testing algorithms before transferring to real hardware.

## Repository Organization

- **`main` branch**: Contains the stable, tested code for deployment on the physical hardware.
- **`feature/real/simple_nav` branch**: Development branch for implementing and testing simple navigation on real robot hardware.
- **`feature/sim/simple_nav` branch (Current)**: Development branch for implementing and testing simple navigation in simulation.
- **`feature/gazebo-simulation` branch**: Contains the simulation logic to test navigation, computer vision, and strategy execution in Gazebo/Ignition before syncing changes to the real robot.
- **`old_feat/real/nav2` branch**: (Deprecated) Kept for historical reference.

## Hardware Setup

Note: This branch is for simulation. The simulated robot is modeled after the real robot hardware:
- **Compute**: Raspberry Pi 5 (8GB RAM) (simulated)
- **OS**: Ubuntu Server 24.04 (simulated)
- **ROS Framework**: ROS 2 (distro matching simulation, e.g., Humble or Iron)

## Getting Started

Prerequisites:
- ROS 2 (Humble or Iron, matching simulation)
- Ubuntu 22.04/24.04
- Gazebo Ignition (or Gazebo Classic, as per ROS 2 distro)

Build:
```
source /opt/ros/<distro>/setup.bash
colcon build
```

Run the simulation with navigation:
```
source install/setup.bash
ros2 launch myrobot_bringup simulated_robot.launch.py
```
(This launch file starts Gazebo and the robot model; navigation can be triggered via the `go_to_goal` action or similar.)

## General Description

This repository provides the core ROS 2 workspace (`simple_bot_ws`) for simulating the custom mobile robot. It is used to test navigation algorithms, computer vision pipelines, and behavior execution in a simulated environment before deploying to the real robot.

## Package Structure

- **`myrobot_description/`**: Contains the URDF, xacro files, and robot state publisher launch setups. Includes Gazebo launch files.
- **`myrobot_bringup/`**: Launch files for executing the robot's core components in simulation and bringing up the hardware interfaces.
- **`myrobot_controller/`**: High-level ROS 2 controllers, multiplexers, and logic files.
- **`myrobot_firmware/`**: Low-level hardware interface layers and micro-controller connection logic (simulated).
- **`myrobot_navigation/`**: Simple Navigation action (in development for simulation).
- **`myrobot_actions/`**: Custom ROS 2 action, service, and message definitions used across the ecosystem.

## Recent Advancements

The simulation stack in this branch has seen the following progress:
- Simple navigation action server implemented and tested in simulation.
- Waypoint following functionality added with simulated sensors.
- Integration with Gazebo for realistic sensor feedback via myrobot_description and myrobot_bringup launch files.

## Known Issues
- [ ] Verify the launch file name for simulation (check myrobot_bringup/launch/simulated_robot.launch.py or myrobot_description/launch/gazebo.launch.py).
- [ ] Test the simple navigation stack under various simulated conditions.
- [ ] Refine the PID tuning for different simulated surfaces and loads.
- [ ] Integrate with computer vision modules for dynamic obstacle detection in simulation.
- [ ] Define and implement game strategy and behavior execution logic in simulation.

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix (based on this branch).
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your fork.
5. Open a pull request to the `feature/sim/simple_nav` branch of this repository.
6. Ensure your pull request passes any automated checks and is reviewed by maintainers.
7. Once approved, maintainers will merge into this branch and later into `main` after testing.

## License

This project is currently unlicensed. Please contact the maintainers for permission to use or distribute the code.