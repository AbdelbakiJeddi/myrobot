# Task: Read and Explain `twist_relay.py`

## Description
Read `src/myrobot_control/myrobot_control/twist_relay.py` end to end. Write a short doc that explains: what topic it reads, what topic it writes, why the message type changes (`Twist` → `TwistStamped`), and how the header timestamp is set. This is the team's smallest ROS 2 node. Reading it teaches the publish/subscribe pattern.

## Desired Output
- New file `tasks/onboarding/twist_relay_explained.md` (or any path the team picks).
- Explains: subscription topic, callback, the `TwistStamped` conversion, the publish.
- One-line summary at the top: "twist_relay bridges raw `/cmd_vel` (Twist) to `/myrobot_controller/cmd_vel` (TwistStamped) because `diff_drive_controller` needs the stamped variant."
- Optional: a tiny mermaid diagram of the data flow.

## Input
- `src/myrobot_control/myrobot_control/twist_relay.py` (33 lines).
- `src/myrobot_bringup/config/controllers.yaml` (line 19: `use_stamped_vel: true`).

## Configuration
- No code change. Read-only task. The deliverable is the explanation.

## Docs Needed
- [ ] `tasks/onboarding/twist_relay_explained.md`.
