# Task: Read the `go_to_goal_server.py` FSM and Draw a State Diagram

## Description
`go_to_goal_server.py` is the most complex node in the project. It implements a 3-state FSM (ALIGN → DRIVE → ORIENT) with PD control. Reading the whole file is too big for a first task. Instead: draw the state machine as a small mermaid diagram and write 3-4 lines per state explaining what it does, what it reads, what it publishes, and how it transitions.

## Desired Output
- New file `tasks/onboarding/go_to_goal_fsm_diagram.md`.
- A mermaid state diagram for the three states and the transitions.
- For each state (ALIGN, DRIVE, ORIENT): purpose, inputs used, output (v, w), exit condition.
- A short "control law" section: which gains are used in which state, pulled from `control_params.yaml`.

## Input
- `src/myrobot_control/myrobot_control/go_to_goal_server.py` (the FSM and `_compute_*` methods).
- `src/myrobot_control/config/control_params.yaml`.

## Configuration
- No code change. Read-only task with a doc deliverable.

## Docs Needed
- [ ] `tasks/onboarding/go_to_goal_fsm_diagram.md`.
