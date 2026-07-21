# Task: Review and Recreate Arduino PID Control Loop + Serial Message

## Description
Review the Arduino firmware that runs the wheel PID. Confirm it matches what ROS 2 sends (command + feedback contract). Recreate the PID loop in a clean form and document the exact serial message format byte-by-byte. Goal: anyone reading the firmware and the ros2_control side can match the two without guessing.

## Desired Output
- Written review of `robot_control.ino` and `feedforward.ino`: what the PID does, where FeedForward enters, how output is clamped, what the loop rate is.
- Recreated PID loop as a clearly commented block (keep one source of truth, but document the structure).
- `serial_protocol.md` in `src/myrobot_hardware/firmware/` listing every byte the firmware reads and writes, with example frames.
- Findings file `review_notes.md` listing anything that looked off (magic numbers, no anti-windup, no derivative filter, etc.).

## Input
- `src/myrobot_hardware/firmware/robot_control/robot_control.ino`
- `src/myrobot_hardware/firmware/feedforward/feedforward.ino`
- `src/myrobot_hardware/firmware/feedforward/tune_pid.ino`
- `src/myrobot_hardware/firmware/feedforward/calibrate.ino`
- `src/myrobot_hardware/src/myrobot_hardware_interface.cpp` (matching side)

## Configuration
- Read-only review. No gains changed in this task. Any tuning change goes to a separate task with a `log/tunings.csv`-style note in the PR.

## Docs Needed
- [ ] `src/myrobot_hardware/firmware/serial_protocol.md` — message format.
- [ ] `src/myrobot_hardware/firmware/review_notes.md` — findings + suggestions.
- [ ] `src/myrobot_hardware/README.md` — link the new docs, note firmware SHA.
