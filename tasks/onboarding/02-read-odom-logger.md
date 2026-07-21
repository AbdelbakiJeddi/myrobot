# Task: Read and Explain `odom_logger.py`

## Description
Read `src/myrobot_utils/myrobot_utils/odom_logger.py` end to end. Write a short doc explaining: what topic it reads (and which one is filtered vs raw), how yaw is extracted from a quaternion, what the `qos_profile_sensor_data` does, and why you would run this node. Great first task to learn odom, quaternions, and QoS.

## Desired Output
- New file `tasks/onboarding/odom_logger_explained.md`.
- Explains: subscription topic, the quaternion → yaw math, the `qos_profile_sensor_data` line, the parameter `odom_topic` and its default.
- One-line summary at the top: "odom_logger prints robot x, y, yaw from `/odometry/filtered` so the team can see the EKF output in the terminal."

## Input
- `src/myrobot_utils/myrobot_utils/odom_logger.py`.
- `src/myrobot_localization/config/ekf.yaml` (line 7: `publish_tf: true`, line 8: `odom_frame: odom`).

## Configuration
- No code change. Read-only task.

## Docs Needed
- [ ] `tasks/onboarding/odom_logger_explained.md`.
