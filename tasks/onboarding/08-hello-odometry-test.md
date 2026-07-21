# Task: Add a "Hello Odometry" Test Node

## Description
Write a tiny ROS 2 node that publishes a constant `Twist` for 3 seconds, then stops. Pair it with a one-line test: launch both the publisher and `odom_logger` for 5 seconds, and check the logger output makes sense. Goal: get a new teammate to write their first publisher, their first launch file, and their first `colcon test`.

## Desired Output
- New node `src/myrobot_control/myrobot_control/drive_forward_3s.py` (publisher).
- New test file `src/myrobot_control/test/test_drive_forward_3s_launch.py` (launches the publisher, checks process exit code 0).
- Entry in `setup.py` (`myrobot_control`) for the new console script.
- PR passes `colcon build` and `colcon test`.

## Input
- `src/myrobot_control/myrobot_control/twist_relay.py` (model for the node structure).
- `src/myrobot_utils/myrobot_utils/odom_logger.py` (the node to verify with).
- `src/myrobot_control/setup.py` (where to register the new entry point).

## Configuration
- Publish `linear.x = 0.1` m/s for 3 seconds, then zero. 10 Hz loop.
- Topic: `/cmd_vel`.
- No params needed in this first version.

## Docs Needed
- [ ] A short README section or comment block at the top of the file explaining the test purpose.
- [ ] `TASK_DONE_TEMPLATE.md` filled: what you built, what test ran, output.
