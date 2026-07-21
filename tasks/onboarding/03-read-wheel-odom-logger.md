# Task: Read and Explain `wheel_odometry_logger.py`

## Description
Read `src/myrobot_utils/myrobot_utils/wheel_odometry_logger.py` end to end. Write a short doc explaining: what topic it reads (`/joint_states`), how it converts joint angles to distance, why it tracks a "start" reference, and what `WHEEL_RADIUS = 0.033` means in physical units. This node is the team's window into whether both wheels travel the same distance.

## Desired Output
- New file `tasks/onboarding/wheel_odom_logger_explained.md`.
- Explains: the subscription, the `left_start_` / `right_start_` reference, the wheel-radius math, the diff metric.
- One-line summary at the top: "wheel_odometry_logger prints how far each wheel has traveled from a reference point — useful for spotting wheels that slip or miss encoder ticks."

## Input
- `src/myrobot_utils/myrobot_utils/wheel_odometry_logger.py`.
- `src/myrobot_bringup/config/controllers.yaml` (line 28: `wheel_radius: 0.033` — should match).

## Configuration
- No code change. Read-only task.

## Docs Needed
- [ ] `tasks/onboarding/wheel_odom_logger_explained.md`.
