# Simulation Guide

This guide describes the camera-only simulation used to test computer-vision code, including ArUco detection and robot pose estimation.

The simulation provides:

- Gazebo with the competition arena and robot model
- RGB camera data
- Wheel odometry from `ros2_control`
- Keyboard teleoperation

The IMU, EKF, and LiDAR are disabled for this setup.

## 1. Prepare the workspace

Open a terminal in the ROS 2 workspace and source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash
```

Build and source the workspace after pulling changes or modifying the robot model:

```bash
colcon build 
source install/setup.bash
```

Run these source commands in every new terminal used with the simulation.

## 2. Start the simulation

```bash
ros2 launch myrobot_bringup simulated_robot.launch.py
```

This starts the Gazebo arena, robot model, wheel controller, camera bridge, RViz, and velocity command relay. It does not start Nav2, an EKF, or a vision algorithm.

## 3. Drive the robot

Install the keyboard teleoperation package once if necessary:

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
```

With the simulation running, start teleoperation in another sourced terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keep the teleoperation terminal focused and use its displayed key bindings. Stop the robot before closing the teleoperation terminal.

## 4. Camera topics

Subscribe your ArUco or pose-estimation node to these topics:

| Topic | Message type | Use |
| --- | --- | --- |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | RGB camera frames |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera calibration and projection data |

The simulated image is `640 x 480` RGB and is published at approximately 30 Hz.

The provided vision package is optional. To run it, use:

```bash
ros2 launch myrobot_vision vision.launch.py
```

For a custom node, start it using the normal command for that package and configure it to use `/camera/image_raw`. Use `/camera/camera_info` when camera calibration is required for pose estimation.

## 5. ArUco and pose-estimation workflow

1. Start the simulation.
2. Start keyboard teleoperation if robot motion is needed.
3. Start the ArUco or pose-estimation node.
4. Subscribe to `/camera/image_raw` for image frames.
5. Subscribe to `/camera/camera_info` for calibration data.
6. Compare or fuse the estimated pose with `/odom` when evaluating results.

The simulation launch does not include a specific computer-vision implementation, so each team can run its own node independently.

## 6. Simulation Screenshots

Add the team screenshots to the paths below and keep the filenames, or update the image links to match the files you add.

### Gazebo Simulation

![Gazebo simulation placeholder](docs/images/gazebo-simulation.png)

*Gazebo arena with the simulated robot.*

### RViz

![RViz placeholder](docs/images/rviz.png)

*RViz view of the robot and its visualization data.*

### Keyboard Teleoperation

![Teleop Twist keyboard placeholder](docs/images/teleop-twist-keyboard.png)

*Keyboard teleoperation running while the robot is simulated.*

