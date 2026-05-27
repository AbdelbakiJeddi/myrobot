# simple_bot_ws — Simulation repository

This workspace contains simulation logic and tools for testing algorithms and strategies for a mobile robot. It is intended for experimenting with:

- Navigation algorithms (planning, localization, mapping)
- Computer vision and perception pipelines
- Strategy and behavior execution (state machines, action servers)

Repository layout (high level):

- `src/` — ROS packages (controllers, description, navigation, bringup, actions, etc.)
- `build/`, `install/`, `log/` — build and install artifacts produced by `colcon`
- `docs/` — documentation and notes

Getting started (typical):

1. Install ROS 2 and required dependencies for your distribution.
2. From the workspace root, build the workspace:

```
source /opt/ros/<distro>/setup.bash
colcon build
```

3. Source the install overlay and run simulation or bringup launch files:

```
source install/setup.bash
ros2 launch <package> <launch_file.launch.py>
```

Notes and conventions:

- Use the `src/` folder for packages that implement algorithms and tests.
- Add simulation worlds, Gazebo/xacro files, and launch files to enable repeatable experiments.
- Keep experiments reproducible by documenting parameters and ROS bag records in `docs/`.

Contributions
- Open pull requests with clear descriptions of experiments and configuration needed to reproduce results.

Contact
- For questions, add an issue describing the experiment and expected behavior.
