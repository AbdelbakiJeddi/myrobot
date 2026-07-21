# Task: Build Gazebo Eurobot-Style Arena

## Description
Create a small Gazebo world that looks roughly like a Eurobot table (rectangular, 2m x 3m, raised border, fixed obstacles, simple ground pattern). The robot will be placed in this arena to test navigation, computer vision, and ArUco detection tasks.

Keep the world minimal: floor + walls + 3-5 fixed obstacles. No dynamic objects yet.

## Desired Output
- `src/myrobot_bringup/worlds/eurobot_arena.sdf` (or `.world` for Gazebo Classic, pick what the team already uses).
- Walls match a 2m x 3m playfield. Height ~ 5cm border (low wall so camera sees over).
- At least 3 distinct obstacles (cubes / cylinders) at known positions.
- `gazebo.launch.py` (or extend `real_robot.launch.py` with a `sim:=true` arg) that loads the world and spawns the robot.
- One screenshot of the arena in RViz + Gazebo saved under `tasks/simulation/`.

## Input
- `src/myrobot_bringup/launch/` — existing launch files.
- `src/myrobot_description/` — robot model to spawn.
- Decide: Gazebo Classic (gazebo_ros) or Ignition Gazebo (ros_gz). Match what the team already has.

## Configuration
- World file: relative path in launch arg `world_file`.
- Robot spawn pose: `(0, 0, 0)` facing +x.
- No physics tuning in this task. Default solver OK.

## Docs Needed
- [ ] `src/myrobot_bringup/README.md` — how to launch the arena.
- [ ] Screenshot in `tasks/simulation/01-eurobot-arena-screenshot.png`.
- [ ] If Gazebo variant chosen, note it in `README.md` so the team doesn't mix Classic and Ignition.
