# Task: Add Camera Sensor on Top of the Robot

## Description
Mount a simulated camera on top of the robot body in the URDF. The camera must publish images on a ROS topic so downstream computer-vision nodes (ArUco, object detection) can use them. Frame must be linked to `base_link` with a fixed transform.

## Desired Output
- New link `camera_link` + joint `camera_joint` mounted on top of the chassis, looking forward.
- Gazebo camera sensor block in the URDF (or sensor xacro) with: resolution 640x480, frame rate 30 Hz, horizontal FOV ~ 70 deg, `camera_info` enabled.
- Topic: `/camera/image_raw` and `/camera/camera_info`.
- RViz view shows the camera frustum and live images.
- Topic visible in `ros2 topic list` after launch.

## Input
- New URDF from task `02`.
- Gazebo variant from task `01` (Ignition uses `<gz:sensor>` block, Classic uses `<sensor type="camera">`).

## Configuration
- Camera mount position: top of body, ~ 5cm above highest chassis point, facing +x.
- Lens FOV: 70 deg horizontal.
- Resolution: 640x480. Frame rate: 30 Hz.
- Noise: keep default (or add small Gaussian if useful for tests).

## Docs Needed
- [ ] `src/myrobot_description/README.md` — camera link, frame, topic.
- [ ] Screenshot in `tasks/simulation/` showing RViz image panel.
