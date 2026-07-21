# Task: Prepare URDF for New Robot Build

## Description
After the hardware survey (task `01`), create a URDF for the new robot build. Use the same xacro structure as `myrobot_description` (split geometry / inertia / ros2_control / sensors). Match physical dimensions and masses to the parts chosen in the survey so the simulation is realistic.

## Desired Output
- `src/myrobot_description/urdf/robot/my_robot_v2.urdf.xacro` (or a separate file under `mechanics/`, the team's call).
- All links: `base_link`, `wheel_left`, `wheel_right`, `caster`, `imu_link`, plus any extras needed by the chosen parts.
- Inertias calculated from real masses (not guessed).
- Loads in RViz and in Gazebo (after task `simulation/03-ros2-control-in-urdf.md` is done).
- Joint limits match motor + encoder specs from the chosen parts.

## Input
- `tasks/mechanics/01-hardware-survey.md` — chosen parts and dimensions.
- `src/myrobot_description/urdf/robot/my_robot.urdf.xacro` — current model to reuse structure.

## Configuration
- Wheel radius, wheel base, body dimensions: from the chosen parts.
- IMU frame: aligned with `base_link`, no offset (or document the offset if the sensor is off-center).
- Use the same xacro split: `common_properties.xacro`, `inertial_macros.xacro`, `robot_ros2_control.xacro`.

## Docs Needed
- [ ] `src/myrobot_description/README.md` — new URDF file, parts it represents, link to survey.
