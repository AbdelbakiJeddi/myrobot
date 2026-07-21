# Task: ArUco Detection + Pose Estimation Node

## Description
Write a ROS 2 node that subscribes to the camera image, detects ArUco markers, and publishes the pose of each detected marker in the camera frame and in the world frame. The pose must be good enough to feed the EKF fusion task.

## Desired Output
- New node `aruco_detector.py` (or C++) in `src/myrobot_control/myrobot_control/` (or a new `myrobot_vision` package if the team creates one).
- Subscribes to `/camera/image_raw` and `/camera/camera_info`.
- Publishes:
  - `/aruco/poses` (custom msg or `geometry_msgs/PoseArray`) — pose of every detected marker in the camera frame.
  - `/aruco/markers` (`visualization_msgs/MarkerArray`) — RViz overlay.
  - `/aruco/image_debug` (`sensor_msgs/Image`) — image with drawn axes for debugging.
- Parameters in YAML: marker dictionary, marker size (m), camera topic, target ID list.

## Input
- Camera from `tasks/simulation/04-camera-on-robot.md` (sim) or real camera (when on rig).
- `tags.yaml` from `tasks/simulation/05-aruco-tags-in-world.md` — marker IDs and sizes.
- Pick: `cv2.aruco` (OpenCV) for detection, or `ros2_aruco` / `aruco_ros` package. Match the team's choice.

## Configuration
- Marker dictionary: `DICT_4X4_50` (lock this in `tasks/simulation/05-...`).
- Marker size: from `tags.yaml` (default 0.10 m).
- Camera topic: `/camera/image_raw`.
- Target IDs: all IDs from `tags.yaml` (or a filtered list passed as param).

## Docs Needed
- [ ] Node README section in the package that hosts it.
- [ ] Screenshot of RViz with markers detected in `tasks/vision/`.
