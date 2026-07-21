# Task: Survey Existing Navigation Approaches for This Robot

## Description
Before going deeper into the simple nav stack, take one pass over what already exists and what other teams / projects have done for the same problem (differential-drive mobile robot, indoor waypoint following, ROS 2 Jazzy, no map / no lidar). Goal: spot reusable patterns, avoid reinventing, and pick a direction for the next nav tasks.

## Desired Output
- Short written survey `survey_notes.md` with these sections:
  1. Current stack summary (what `myrobot_control` + `myrobot_hardware` do today, in 1 page).
  2. Reusable parts already in ROS 2 Jazzy: `nav2_simple_navigator`, `topic_tools`, `twist_mux`, behavior trees, `nav2_rotation`.
  3. Other open projects worth looking at: ros2-planning/navigation2 examples, husky/clearpath demos, small-scale academic stacks.
  4. Recommendations: keep simple stack, replace X with Y, or stop and switch to Nav2.
- Decision section at the end: which direction the team should take for the next 3 nav tasks.

## Input
- `README.md`, `GENERAL_RULES.md`, `src/myrobot_control/`, `src/myrobot_hardware/`.
- Web search for: "ROS 2 Jazzy simple waypoint follower", "differential drive rotate to heading PID", "nav2 vs custom simple navigator".

## Configuration
- Read-only research task. No code change. Deliverable is the survey doc.

## Docs Needed
- [ ] `tasks/navigation/05-survey-notes.md` (or wherever the team prefers) — full survey.
- [ ] Update `tasks/navigation/README.md` (create if missing) with a one-paragraph TL;DR and link to the survey.
