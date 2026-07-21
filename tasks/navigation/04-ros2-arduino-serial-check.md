# Task: Check Serial Message Between ros2_control and Arduino

## Description
Trace the exact data path: `ros2_control` command → hardware interface → serial write → Arduino → serial read → wheel output. Confirm the message format on both sides is identical (endianness, separator, units, ranges). Find any place where a unit mismatch (rad/s vs PWM, ticks vs rad) or framing bug could cause wrong behavior on the rig.

## Desired Output
- Side-by-side table: `ros2_control` field ↔ Arduino variable ↔ units ↔ scaling.
- List of confirmed matches and any mismatches found.
- If a bug is found, a short repro note (how to trigger it, what to expect, what happens instead).
- Output: `src/myrobot_hardware/docs/ros2_arduino_wire.md`.

## Input
- `src/myrobot_hardware/src/myrobot_hardware_interface.cpp` — write side.
- `src/myrobot_hardware/include/myrobot_hardware/myrobot_hardware_interface.hpp` — types and interface.
- `src/myrobot_hardware/firmware/robot_control/robot_control.ino` — read side.
- `src/myrobot_hardware/firmware/feedforward/feedforward.ino` — read side.
- `src/myrobot_hardware/myrobot_hardware_interface.xml` — exposed joints/interfaces.

## Configuration
- Read-only investigation. No code change in this task. Bugs found → separate ClickUp tasks.

## Docs Needed
- [ ] `src/myrobot_hardware/docs/ros2_arduino_wire.md` — wire contract.
- [ ] Bugs found → ClickUp tasks, link back here.
