# Task: Review URDF and Create Clean Replacement

## Description
Review the current URDF/xacro files in `src/myrobot_description/urdf/`. Find dead links, wrong inertias, hardcoded values, broken joint limits, or anything that would break in simulation. Then create a clean, well-commented URDF/xacro that the simulator can load without warnings.

## Desired Output
- `review_notes.md` listing every issue found in the current URDF.
- New `src/myrobot_description/urdf/robot/my_robot_v2.urdf.xacro` (or merged into `my_robot.urdf.xacro`) with:
  - Correct mass + inertia for every link.
  - All joint limits in valid ranges.
  - No leftover comments or dead links.
  - Xacros split by role (geometry, inertia, ros2_control, sensors).
- Renders in RViz with no errors and shows the full kinematic tree.

## Input
- `src/myrobot_description/urdf/robot/my_robot.urdf.xacro`
- `src/myrobot_description/urdf/robot/my_robot_homemade.xacro`
- `src/myrobot_description/urdf/robot/common_properties.xacro`
- `src/myrobot_description/urdf/robot/inertial_macros.xacro`
- `src/myrobot_description/urdf/robot/robot_ros2_control.xacro`

## Configuration
- Wheel radius, wheel base, body dimensions: read from current xacro, keep the same numbers. This task is cleanup, not redesign.
- If a number is wrong, flag it in `review_notes.md` but fix it only if the change is obvious (e.g. inertia = 0).

## Docs Needed
- [ ] `src/myrobot_description/urdf/robot/review_notes.md`.
- [ ] `src/myrobot_description/README.md` updated to point at the new URDF.
