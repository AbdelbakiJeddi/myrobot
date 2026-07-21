# Task: Read and Explain `waypoints.yaml` + `go_to_goal_client.py`

## Description
Read `src/myrobot_control/config/waypoints.yaml` and `src/myrobot_control/myrobot_control/go_to_goal_client.py` together. Write a short doc explaining: how the waypoints are declared as parameters (`goal_0.x`, `goal_1.y`, etc.), how the client walks through them, how the action goal is built, what `yaw_in_degrees` does, and what `goal_hold_time` does. This is how a real nav mission gets launched.

## Desired Output
- New file `tasks/onboarding/waypoints_and_client_explained.md`.
- Sections: param format, loader loop, action goal build, hold-time behavior, success / failure handling.
- One-line summary at the top: "waypoints.yaml lists the mission, go_to_goal_client.py walks it. Each entry becomes one action goal sent to `navigate_to_pose`."

## Input
- `src/myrobot_control/config/waypoints.yaml`.
- `src/myrobot_control/myrobot_control/go_to_goal_client.py`.
- `src/myrobot_interfaces/action/NavigateToPose.action`.

## Configuration
- No code change. Read-only task.

## Docs Needed
- [ ] `tasks/onboarding/waypoints_and_client_explained.md`.
