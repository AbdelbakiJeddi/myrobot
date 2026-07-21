# Task: Survey Available Hardware for New Robot Build

## Description
Search the market for the hardware the team needs to build a new (or replace a worn-out) mobile robot: wheel encoders, IMU, batteries, chassis material. Focus on parts that are easy to buy locally or online, ROS 2 compatible, and within hobbyist budget. End with a shortlist the team can order.

## Desired Output
- `hardware_survey.md` with one table per category: encoder, IMU, battery, chassis material.
- Each row: vendor / model / price / link / ROS 2 compatibility note / pros / cons.
- A "Top 3 per category" pick list at the end.
- Recommendation block: one full bill of materials (BOM) for a build equivalent to the current robot.

## Input
- Current robot specs from `README.md` (Pi 5, Arduino, MPU6050, 2 DC motors with encoders).
- Current `myrobot_hardware` package to see what interfaces the firmware already supports.

## Configuration
- Read-only research task. No code change. Web search is the main input.

## Docs Needed
- [ ] `tasks/mechanics/01-hardware-survey.md`.
- [ ] If a part is selected, update `src/myrobot_hardware/README.md` with the chosen part + link.
