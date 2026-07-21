# Task: Integrate ros2_control into URDF

## Description
Make sure the URDF exposes the right ros2_control interfaces so `ros2_control` can drive the wheels in simulation the same way it does on the real robot. Reuse the existing `robot_ros2_control.xacro` if possible; otherwise rewrite it cleanly.

## Desired Output
- `ros2_control` `<hardware>` block for the sim plugin (`gz_ros2_control` if using Ignition, `gazebo_ros2_control` for Classic).
- Two wheel joints exposed as `velocity` command interfaces.
- Wheel encoder joints exposed as `position` (or `velocity`) state interfaces.
- `controller_manager` config (already in `myrobot_control`) loads `diff_drive_controller` and `joint_state_broadcaster`.
- Robot moves in the arena when a `Twist` is published.

## Input
- `src/myrobot_description/urdf/robot/robot_ros2_control.xacro`
- `src/myrobot_hardware/src/myrobot_hardware_interface.cpp` (real-side interface — to mirror in sim)
- `src/myrobot_control/config/control_params.yaml`
- Decide Gazebo variant first (see task `01`).

## Configuration
- Sim hardware plugin name: `gz_ros2_control/GZSystem` (Ignition) or `gazebo_ros2_control/GazeboSystem` (Classic).
- Joint names: match the new URDF wheel joint names from task `02`.
- Command interface: `velocity` for each wheel.
- State interfaces: `position` + `velocity` per wheel.

## Docs Needed
- [ ] `src/myrobot_description/README.md` — section on sim ros2_control setup.
- [ ] `src/myrobot_control/README.md` — controller config used.
