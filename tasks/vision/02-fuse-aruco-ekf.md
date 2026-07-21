# Task: Fuse ArUco Poses into EKF

## Description
Add the ArUco marker poses as measurements to the existing `robot_localization` EKF so the robot's global pose estimate gets corrected when a marker is visible. The EKF already fuses wheel odometry + IMU. This task adds a third source: known marker world poses from the detector.

## Desired Output
- New EKF config (or update of the current one) that takes a PoseWithCovariance input from the ArUco node.
- Topic for ArUco input: `/aruco/world_poses` (PoseWithCovarianceStamped, world frame).
- World frame: match the EKF's `world_frame` param.
- Reasonable covariance on the input so a bad detection doesn't kill the estimate.
- Before/after comparison: show EKF drift on long run without ArUco vs with ArUco.

## Input
- EKF config in `src/myrobot_localization/config/ekf.yaml`.
- `/aruco/world_poses` from task `vision/01-aruco-detector-node.md`.
- `tags.yaml` — known marker world poses (ground truth).

## Configuration
- New EKF input: `aruco` sensor, world frame, pose with covariance.
- `pose_covariance` per dimension: start at `[0.05, 0.05, 0.0, 0.0, 0.0, 0.1]` and tune from logs.
- `sensor_timeout`: ~ 0.5 s — drop the measurement if a marker hasn't been seen in 500 ms.

## Docs Needed
- [ ] `src/myrobot_localization/README.md` — new sensor input, topic, frame, covariance.
- [ ] `log/`-style log capture from before/after run (compare drift over 1 min).
