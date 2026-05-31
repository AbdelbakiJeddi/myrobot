# GoToGoal Action Server

## Overview
The `go_to_goal_server.py` node is a **non-blocking, asynchronous navigation action server** that enables a robot to navigate to a goal position with a desired final heading. It uses a finite state machine (FSM) to execute the navigation task.

## What It Does
- **Accepts navigation goals** via the `navigate_to_pose` ROS2 action
- **Subscribes to odometry** (`/odometry/filtered`) to track the robot's current pose
- **Executes a 3-state FSM** to move the robot from its current position to a target position with a specified heading:
  1. **ALIGN** — Rotate in place to face the goal position
  2. **DRIVE** — Drive forward toward the goal while correcting heading drift
  3. **ORIENT** — Rotate to match the final desired heading

## Key Features
- **Asynchronous execution** — Runs in a separate thread using `MultiThreadedExecutor` with reentrant callback groups
- **Real-time feedback** — Publishes current state and distance-to-goal during navigation
- **Configurable parameters** — Control rates, gains, max velocities, and tolerances
- **Cancellation support** — Can be interrupted by external cancel requests
- **Result reporting** — Returns final position and heading errors upon completion

## IO Interfaces
| Type | Topic/Action | Message |
|------|--------------|---------|
| **Subscribe** | `/odometry/filtered` | `nav_msgs/Odometry` |
| **Publish** | `/myrobot_controller/cmd_vel` | `geometry_msgs/TwistStamped` |
| **Action Server** | `navigate_to_pose` | `myrobot_actions/NavigateToPose` |

## Control Strategy
- Uses **proportional-derivative-like control** with tunable gains (`kv`, `kw`)
- Implements **heading error correction** during forward motion to prevent drift
- Clamps velocities to safe limits (`v_max`, `w_max`)
