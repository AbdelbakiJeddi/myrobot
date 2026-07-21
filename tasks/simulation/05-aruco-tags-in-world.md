# Task: Add ArUco Tags to the Sim World

## Description
Place a set of ArUco markers in the Gazebo arena at known world positions. Markers must be visible to the on-robot camera and detectable by a standard `ros2_aruco` (or `aruco_ros`) node. Use distinct IDs per marker so the vision pipeline can identify obstacles / goals by ID.

## Desired Output
- World file (from task `01`) updated with at least 4 ArUco tags as thin planes on obstacles or arena walls.
- Each tag has: known world pose, unique ID, known physical size (meters).
- A `tags.yaml` (or json) listing every tag: id, pose, size, semantic name (e.g. `goal_north`, `obstacle_1`).
- `aruco_ros` (or equivalent) node running, publishing detected poses on `/aruco_poses`.
- RViz visualization shows detected tags in the camera image.

## Input
- World file from task `01`.
- Camera from task `04` — must see the tags.
- Pick: `ros2_aruco` (active fork) or `aruco_ros` classic. Match what the team already uses.

## Configuration
- Marker dictionary: `DICT_4X4_50` (or whatever the team picks — fix it here, document it).
- Marker physical size: 0.10 m (10 cm) — adjust if camera FOV makes it too small at arena scale.
- Tag IDs: pick 4 IDs that don't clash with anything else (e.g. 0, 1, 2, 3).
- Tag world poses: stored in `tags.yaml`, loaded by both world file and the detection config.

## Docs Needed
- [ ] `src/myrobot_bringup/worlds/tags.yaml` — id, pose, size, name.
- [ ] `src/myrobot_control/README.md` (or a new `myrobot_vision/README.md` if CV package gets created) — how to run ArUco detection in sim.
- [ ] Screenshot in `tasks/simulation/` showing the camera image with detected markers overlaid.
