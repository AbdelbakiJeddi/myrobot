# Task: Add a README to `myrobot_control`

## Description
There is no `src/myrobot_control/README.md`. Write one that lists every node in the package, what it does, its topics in/out, and its parameters. The team uses this file to onboard new members. It's a pure-doc task — no code change.

## Desired Output
- New file `src/myrobot_control/README.md` with one section per node:
  - `twist_relay.py` — purpose, topic in, topic out.
  - `go_to_goal_server.py` — purpose, action name, params from `control_params.yaml`, topic in, topic out.
  - `go_to_goal_client.py` — purpose, params from `waypoints.yaml`.
  - `simple_navigator.py` — purpose, why it exists (open-loop square test), warn that it's diagnostic, not for real missions.
- Each section: 3-6 lines, no code blocks bigger than the topic names.
- A "How to run" section at the top: `ros2 launch myrobot_control control.launch.py`.

## Input
- `src/myrobot_control/myrobot_control/twist_relay.py`
- `src/myrobot_control/myrobot_control/go_to_goal_server.py`
- `src/myrobot_control/myrobot_control/go_to_goal_client.py`
- `src/myrobot_control/myrobot_control/simple_navigator.py`
- `src/myrobot_control/config/control_params.yaml`
- `src/myrobot_control/config/waypoints.yaml`
- `src/myrobot_control/launch/control.launch.py`

## Configuration
- No code change. Read-only task with a doc deliverable.

## Docs Needed
- [ ] `src/myrobot_control/README.md`.
