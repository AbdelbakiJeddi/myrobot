# Team Handover — myrobot

> **Date:** September 2026
> **Project:** Eurobot 2026 Mobile Robot Navigation
> **Active Branch:** `feature/real/simple_nav`
> **Platform:** Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy

---

## 1. Project Overview

This is a **ROS 2 navigation stack for a physical differential-drive robot** competing in Eurobot 2026. The robot uses dead-reckoning (no lidar, no AMCL, no map) — just EKF-fused odometry + ordered waypoints to navigate an arena.

**Core idea:** The robot starts at a fixed boot position. Waypoints are offsets from that boot position. A `simple_navigator` node follows waypoints using a trapezoid velocity profiler + PID heading control. Arduino firmware runs a per-wheel PID with feedforward at 50 Hz.

---

## 2. Hardware Setup

| Component | Details |
|---|---|
| **SBC** | Raspberry Pi 5, Ubuntu 24.04 |
| **Microcontroller** | Arduino (flashed with `robot_control.ino`) |
| **Motor Driver** | L298N |
| **Motors** | 2× DC motors with encoders (900 ticks/rev) |
| **IMU** | MPU6050 (I2C bus 1, address 0x68) |
| **Serial** | `/dev/ttyUSB0`, 115200 baud |
| **Other** | 2 caster wheels, optional camera/lidar in URDF (not active) |

---

## 3. Repository Structure

```
myrobot/                          # colcon workspace root
├── README.md                     # Project documentation
├── TODO.md                       # Roadmap & development rules (READ THIS)
├── HANDOVER.md                   # This file
├── src/                          # 7 ROS 2 packages
│   ├── myrobot_bringup/          # Central launch + configs, maps, waypoints, rviz
│   ├── myrobot_control/          # Navigation: simple_navigator, twist_relay
│   ├── myrobot_description/      # URDF/xacro robot model + RViz display
│   ├── myrobot_hardware/         # C++ ros2_control plugin + Arduino firmware
│   ├── myrobot_interfaces/       # Custom action (NavigateToPose) + msg (MotorFeedback)
│   ├── myrobot_localization/     # MPU6050 IMU driver + EKF config
│   └── myrobot_utils/            # Diagnostics: odom_logger, path_visualizer, PID tuner
└── build/ install/ log/          # colcon build artifacts
```

---

## 4. Package Responsibilities

| Package | What It Does | Key Files |
|---|---|---|
| **myrobot_interfaces** | Custom ROS messages and actions | `NavigateToPose.action`, `MotorFeedback.msg` |
| **myrobot_description** | Robot model (URDF/xacro), RViz visualization | `urdf/robot/my_robot.urdf.xacro`, `display.launch.py` |
| **myrobot_hardware** | ros2_control SystemInterface plugin (C++) + Arduino firmware | `myrobot_hardware_interface.cpp`, `robot_control.ino` |
| **myrobot_localization** | IMU driver + Extended Kalman Filter | `mpu6050_driver.py`, `ekf.yaml` |
| **myrobot_control** | Navigation FSM, velocity profiler, PID heading, twist relay | `simple_navigator.py`, `twist_relay.py` |
| **myrobot_utils** | Diagnostic tools (logging, visualization, PID tuning) | `odom_logger.py`, `path_visualizer.py` |
| **myrobot_bringup** | Main launch entry point, all config files, waypoints | `real_robot.launch.py`, `controllers.yaml` |

---

## 5. How to Build and Run

### Build
```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

### Run (Full Robot)
```bash
# Full stack (navigation optional with launch_navigation:=true)
ros2 launch myrobot_bringup real_robot.launch.py

# Navigation only (hardware must already be running)
ros2 launch myrobot_control control.launch.py

# URDF/RViz dev test
ros2 launch myrobot_description display.launch.py
```

---

## 6. Data Flow (Who Talks to Who)

```
Arduino (50 Hz PID + FeedForward)
   ↕ Serial: "L:<vel>,R:<vel>" ↔ "L:<ticks>,<vel>,R:<ticks>,<vel>"
myrobot_hardware_interface.cpp (ros2_control SystemInterface)
   → State interfaces: wheel position + velocity
   → myrobot_controller (diff_drive_controller)
      → publishes /myrobot_controller/odom
      ← consumes /myrobot_controller/cmd_vel (TwistStamped)

MPU6050 IMU → /imu/data_raw (100 Hz)
   → imu_filter_madgwick → /imu/out
   → EKF fuses IMU + wheel odom → /odometry/filtered

simple_navigator.py
   → subscribes /odometry/filtered
   → publishes /myrobot_controller/cmd_vel

twist_relay.py
   → /cmd_vel (Twist) → /myrobot_controller/cmd_vel (TwistStamped)
```

---

## 7. Navigation Stack — Current State

### What's Working
- **`simple_navigator.py`** (388 lines) — the active navigation core
  - FSM: `NEED_POSE → ALIGN → DRIVE → ORIENT → DONE`
  - Trapezoid velocity profile: `v = min(v_max, √(2a·dist), √(2a·to_go))`
  - PID heading control with anti-windup, integral clamp, min-w ramp
  - Re-align if heading error > 0.35 rad
  - Watchdogs: odom timeout 0.5s, state timeout 10s

### What's In Progress (Stages from TODO.md)
- **Stage 0:** Odom honesty verification (verify EKF, wheel calibration)
- **Stage 1:** ✅ Rotate to heading (completed)
- **Stage 2:** Drive straight with profiler + PID
- **Stage 3:** Single waypoint (ALIGN + DRIVE combined)
- **Stage 4:** Multi-waypoint mission list
- **Stage 5:** Safety protections (odom stale, state timeout, shutdown)
- **Stage 6:** Wrap as action server (replaces legacy go_to_goal_server)

### Legacy Code (Deprecated)
- `go_to_goal_server.py` and `go_to_goal_client.py` are **legacy** — reference only
- `simple_navigator.py` is the new core; legacy files will be deleted after Stage 6

---

## 8. Configuration Files

| File | Purpose |
|---|---|
| `config/controllers.yaml` | controller_manager + diff_drive config |
| `config/simple_navigator.yaml` | Navigator params (speed, PID gains, tolerances) |
| `config/control_params.yaml` | Legacy go_to_goal params |
| `config/waypoints.yaml` | Waypoint definitions |
| `config/ekf.yaml` | EKF fusion config (IMU + wheel odom) |

**Key params to know:**
- `wheel_separation: 0.34m`, `wheel_radius: 0.033m`
- EKF: IMU owns yaw, wheel odom owns x/y
- Navigator: v_max, a_max, kp/ki/kd for heading, tolerances

---

## 9. Firmware Details

### robot_control.ino (Active)
- 50 Hz per-wheel PI + feedforward: `pwm = PI_out + kS·sign(v) + kV·|v|`
- Serial protocol: `L:<vel>,R:<vel>` commands, `L:<ticks>,<vel>,R:<ticks>,<vel>` feedback
- 0.5s command watchdog (stops if no commands)
- Pin mapping: L298N pins 5–10, encoders pins 2/A1 and 3/4
- **Note:** LEFT_WHEEL = 1, RIGHT_WHEEL = 0 (check `myrobot_hardware_interface.cpp`)

### pid_tune.ino (Tuning Tool)
- Extended variant accepting live gain messages for on-bench tuning
- Used with `pid_gains_tunning.py` + PlotJuggler/pyqtgraph GUI

### Tuning Workflow
1. Raise robot off ground
2. Sweep PWM to characterize motors
3. Fit kS (static friction) and kV (velocity constant) feedforward gains
4. Step-response test for PID gains
5. Document old vs new values in PR

---

## 10. Known Issues & Stale References

### Active Issues
- **PID tuning** needs refinement (calibrate left/right feedforward independently)
- **EKF** relies on wheel odom yaw + gyro; consider magnetometer for absolute heading
- **Full hardware-in-the-loop navigation test** pending
- **Forward-only vs reverse** decision not yet made for 180° turns

### Stale/Duplicate Code
- `real_robot.launch.py` (modern) and `hardware.launch.py` (legacy) start overlapping components — pick one
- `build/` and `install/` contain artifacts from removed packages (`myrobot_actions`, `myrobot_controller`, etc.)
- `.vscode/settings.json` references removed `myrobot_actions` package
- Firmware README references `feedforward/` directory that no longer exists

### Missing Pieces
- **No unit/integration tests** — only linting; hardware-in-the-loop validation
- **No CI/CD files** in repo (conventions mention CI but no GitHub Actions)
- **Camera driver** not implemented (ArUco vision planned for later)
- **Ultrasonic sensors** not wired (proximity safety planned for later)

---

## 11. Roadmap (What's Next)

### Immediate Priorities
1. **Complete Stages 2–3:** Straight drive + single waypoint navigation
2. **Complete Stage 4:** Multi-waypoint mission list
3. **Complete Stage 5:** Safety protections
4. **Complete Stage 6:** Wrap as action server, delete legacy code

### Medium-Term (After Navigation Works)
5. **ArUco Vision (Section 8):** Absolute pose anchors to kill odom drift
6. **Ultrasonic Proximity (Section 9):** Safety stop + wall-follow
7. **Strategy Setter (Section 10):** The "brain" — FSM + rule table for Eurobot mission

### Mission Strategy (Eurobot 2026)
```
Start → Pick 2 crates → Deliver → Pick 2 more → Deliver → Return to nest
+ Drift correction via ArUco anchors during driving
+ Deadline law: reserve last X seconds for return
```

---

## 12. Development Conventions

- **One task = one PR**
- Branch naming: `type/CU-id-kebab-slug` (e.g., `feat/CU-abc123-goal-tolerance`)
- Conventional Commits for messages
- **Tuning changes:** Document old value, new value, why, and link test run — NEVER silent retune
- Templates: `NEW_TASK_TEMPLATE.md` (task creation), `TASK_DONE_TEMPLATE.md` (PR body)

---

## 13. Quick Reference — Key Commands

```bash
# Check topic list
ros2 topic list

# Check node list
ros2 node list

# View odom data
ros2 topic echo /odometry/filtered

# View IMU data
ros2 topic echo /imu/out

# Check controller status
ros2 controller list

# PID tuning (connects to Arduino via serial)
ros2 run myrobot_utils pid_gains_tunning

# Log odom for analysis
ros2 run myrobot_utils odom_logger
```

---

## 14. Contacts & Resources

- **TODO.md** — The authoritative roadmap and rules (268 lines, very detailed)
- **README.md** — Project overview and contributing guide
- **firmware/README.md** — Motor tuning workflow
- **my_tasks/pid-tuning-gui.md** — PID tuning GUI spec

---

## Summary for Incoming Team

**You're taking over a half-built ROS 2 navigation stack for a Eurobot robot.** The core `simple_navigator` exists and handles single-waypoint navigation. What's missing is multi-waypoint missions, safety protections, and wrapping it as an action server. After that, the big features are ArUco vision for drift correction and a strategy brain for the full mission.

**Start by:**
1. Reading `TODO.md` — it's the detailed roadmap
2. Building and running the stack on the Pi 5
3. Testing Stage 2–3 navigation on the rig
4. Working through the stages sequentially

**The robot drives, turns, and follows simple waypoints. Your job is to make it follow complex missions reliably.**
