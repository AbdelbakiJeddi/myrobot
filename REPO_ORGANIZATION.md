# Repository Organization

## Branch Naming Conventions
- `main`: stable branch
- `feature/<feature-name>`: for new features
- `bugfix/<issue>`: for bug fixes
- `release/<version>`: for release preparation

## Current Branch (as of initialization)
- main: contains the nav2_stack_integration work

## Folder Structure
- `src/`: ROS 2 packages
  - `myrobot_actions/`: action definitions
  - `myrobot_bringup/`: launch files for bringing up the robot
  - `myrobot_controller/`: controller nodes and configurations
  - `myrobot_description/`: robot model (URDF, meshes)
  - `myrobot_firmware/`: firmware for microcontroller
  - `myrobot_navigation/`: navigation stack configurations

## Configuration Files
- Launch files are in `*/launch/` directories
- Config files are in `*/config/` directories

## Build Artifacts
- `build/`, `install/`, `log/` are excluded by .gitignore

## Documentation
- `docs/`: for design documents, reviews, etc.
- `.remember/`: for internal memory (excluded by .gitignore)

## Other
- `.vscode/`: VS Code settings (currently not excluded, consider adding to .gitignore if user-specific)