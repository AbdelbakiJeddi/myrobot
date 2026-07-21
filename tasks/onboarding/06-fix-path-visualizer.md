# Task: Fix the `path_visualizer.py` Broken File Path

## Description
`src/myrobot_utils/myrobot_utils/path_visualizer.py` reads a CSV from `myrobot_bringup/waypoints/0_track.csv`. That file does not exist, and the `waypoints/` directory does not exist either. The node always logs `FileNotFoundError`. Fix the path lookup so it points to a real file, or convert the node to read the YAML waypoints format that already exists.

## Desired Output
- Pick ONE of:
  - (a) make `path_visualizer.py` read `src/myrobot_control/config/waypoints.yaml` and plot the (x, y) goals + their headings, OR
  - (b) point it at an existing CSV (none today — would need a generator), OR
  - (c) remove the node if it's not used. Add a one-line comment in the file explaining why.
- Whatever you pick, the node must not crash on launch. Default file picked up by the `waypoints_file` param must exist.
- A screenshot of the plot saved as `tasks/onboarding/path_visualizer_fixed.png` (if (a) or (b)).

## Input
- `src/myrobot_utils/myrobot_utils/path_visualizer.py` (broken lookup at line 21).
- `src/myrobot_control/config/waypoints.yaml` (real data to plot if going with option (a)).
- `myrobot_bringup/waypoints/` (does not exist — `ls` to confirm).

## Configuration
- Keep the same `waypoints_file` parameter, but make the default path real.
- For option (a): parse the YAML keys `goal_0`, `goal_1`, … and read `x`, `y`, `yaw` from each.

## Docs Needed
- [ ] `src/myrobot_utils/README.md` — what the node plots and where the data comes from.
- [ ] The screenshot if (a) or (b).
