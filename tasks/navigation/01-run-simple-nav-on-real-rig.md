# Task: Run Simple Nav Stack on Real Robot

## Description
Validate the full simple navigation stack (GoToGoal action server + waypoint client + PID with FeedForward) on the real hardware. Confirm the robot can drive through a small waypoint set without manual intervention. Surface bugs, tuning gaps, or hardware issues before moving to next nav task.

## Desired Output
- Robot drives through ≥ 3 waypoints in sequence on the real rig.
- Each waypoint reached within tolerance (no manual nudging).
- `TASK_DONE_TEMPLATE.md` filled with observed behavior, any issues, and tuning changes.
- Issues found → ClickUp tasks created and linked from this doc.

## Input
- Branch: `feature/real/simple_nav` (already on `main` after merge).
- Waypoints: `src/myrobot_bringup/config/waypoints.yaml`.
- Current known issue: left/right FeedForward not calibrated independently.
- Hardware: Pi 5, Arduino with PID + FeedForward, MPU6050, wheel encoders.

## Configuration
- Launch: `ros2 launch myrobot_bringup real_robot.launch.py launch_navigation:=true`.
- EKF config: `src/myrobot_localization/config/ekf.yaml`.
- PID gains: Arduino firmware (FeedForward on).
- Waypoint tolerance: from `control.launch.py` params.

## Docs Needed
- [ ] `TASK_DONE_TEMPLATE.md` filled with rig run results.
- [ ] Tuning changes (if any) documented in PR body.
- [ ] Bugs found → ClickUp tasks, linked back here.
