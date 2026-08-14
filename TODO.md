# TODO — myrobot

> STONE TABLE OF WORK. READ. DO. CHECK. DONE.
> One task = one PR. Use docs/templates. See CONVENTIONS (bottom).

---

## 1. NAV — make robot go to points (dead-reckoning)

NO lidar. NO map frame. NO AMCL. NO planner. Just EKF odom + waypoints.
Forget go_to_goal_*. Reference only. New core: `simple_navigator.py`.

### RULES (decided, don't re-argue)

- odom frame = arena. Boot at fixed spot+facing. Waypoints = offsets from boot.
- Waypoints ARE the path. Points only. No splines. No smoothing. Ordered list.
- Each waypoint: `{x, y, yaw_target, task_slot}`. task_slot = future "do thing here", now None.
- Speed: trapezoid profiler. v = min(v_max, sqrt(2*a_max*dist), v_prev + a_max*dt)
  → accel, cruise, brake to zero AT the point. No overshoot. No crawl.
- Heading: PID. w = kp*e + ki*∫e − kd*yaw_rate. Integral kills steady drift (gyro bias).
  Anti-windup: clamp integral, freeze when saturated or big error.
- Rotate via PD helper with min-w ramp (near-small-error stall fix).
- Settled = |err| < tol AND |rate| < thresh. Never skip point while moving.
- Re-align if |err| > threshold while driving.

### STATE FLOW

NEED_POSE → ALIGN → DRIVE → (ORIENT) → NEXT → DONE
  ALIGN = spin to face point (PID). DRIVE = go straight w/ profiler+PID.
  ORIENT = optional, spin to final yaw. NEXT = advance, hold, or stop.

### Safety (all stages from Stage 1 on)

- Odom stale → STOP + abort.
- State timeout / no progress → STOP + abort.
- Always shut down with v=0, w=0.

### CHECKLIST

- [ ] STAGE 0 — verify odom is honest
  - [ ] EKF really uses IMU yaw? (ekf.yaml)
  - [ ] Drive 5 m straight. Measure real vs commanded. Fix wheel_radius/separation.
  - [ ] Spin 90/180/270. Yaw true?
      (THIS IS THE FOUNDATION. SKIP IT = WRONG GOALS.)
- [x] STAGE 1 — ROTATE to heading
  - [x] FSM skeleton + NEED_POSE gate in simple_navigator.py
  - [x] ROTATE + theta param + steer_pd() (kp*err − kd*yaw_rate, clamp, min-w ramp)
  - [x] Settled exit: |err| < tol AND |yaw_rate| < thresh
  - [ ] TEST: spin to 90°, no wobble. `-p theta:=1.5708`
- [ ] STAGE 2 — DRIVE straight (profiler + PID)
  - [ ] v = min(v_max, sqrt(2*a_max*dist), ramp)
  - [ ] steer_pd() → steer_pid() (add ki, anti-windup)
  - [ ] Settled exit: dist < tol AND |speed| < thresh
  - [ ] TEST: 2 m straight. No drift. No overshoot.
- [ ] STAGE 3 — one point = ALIGN + DRIVE
  - [ ] bearing = atan2(dy,dx) → ALIGN → DRIVE profiler+PID
  - [ ] re-align if heading err too big
  - [ ] TEST: several scattered points from one start
- [ ] STAGE 4 — point list (mission)
  - [ ] wp_n.x/y[/yaw] params, index pointer, hold time, stop at last
  - [ ] optional ORIENT per point
  - [ ] TEST: 4-point lap
- [ ] STAGE 5 — protections
  - [ ] odom stale stop+abort
  - [ ] per-state timeout / no-progress stop+abort
  - [ ] shutdown publishes v=0 w=0
- [ ] STAGE 6 — becomes an ACTION SERVER (after testing + tuning)
  - [ ] Wrap simple_navigator as `navigate_to_pose` action server
      (goal = waypoint from message, feedback, cancel). Replaces go_to_goal_server.
      Control stays profile+PID. See Section 10 — the action server is its
      interface to the strategy setter.
  - [ ] Kill go_to_goal_server.py + go_to_goal_client.py once it lands.

### PARAMS (grow each stage)

- linear: v_max, a_max · pos_tol, lin_thresh
- rotate: kp, ki, kd · w_max, min_w_rotate · align_tol, ang_vel_thresh, realign_threshold
- safety: odom_timeout, max_state_time

### OPEN

- [x] ORIENT every point or only last? → Every point has yaw_target (mission waypoint).
- [ ] Forward only, or reverse for 180°?
- [ ] Kill goal_x/goal_y, use wp_n only? → TODO update: single-wp (wp_x/wp_y) is current;
      mission = ordered list of wp_n + task_slot (Stage 4 / §10).
- [ ] CORNER RE-ZERO: navigator needs a "bump to wall & re-zero odom" ability.
      Stage/driver decision: who owns the bump — navigator primitive or strategy?

### On odom honesty (don't forget)

- Control PID only makes robot DO what it thinks. If belief (odom) is wrong,
  pose is wrong. Error grows with distance. Kill it with:
  1) calibration (Stage 0)  2) ArUco anchor (Section 8)  3) short legs.

---

## 2. LAUNCH — clean up

- [ ] DUPLICATION: real_robot.launch.py and hardware.launch.py start the SAME stuff
      (state pub, controller_manager, spawners, twist_relay). Pick ONE owner. Other includes it.
- [ ] MAGIC TIMERS: TimerAction 2/4/6/8/10 s everywhere. Fragile. Use OnProcessExit/events.
- [ ] PATHS: string concat / GetPackageShare hack. Use PathJoinSubstitution + os.path.join.
- [ ] control.launch.py: FindPackageShare().find()+'/config' inline. Kill it.
- [ ] Which launch is THE entrypoint? real_robot or hardware? Pick, document.
- [ ] display.launch.py still works for URDF/RViz test?
- [ ] localization.launch.py: is mpu6050_driver.py console_script in setup.py?

---

## 3. NODES & TOPICS — who talks to who

- [ ] Make map: `ros2 node list`, `ros2 topic list`. Draw the graph. Save it.
- [ ] waypoints/*.csv (0/1/8/S/SS_track) — big odom logs. Used by anyone? Dead? Delete or move.
- [ ] myrobot_utils nodes (odom_logger, path_visualizer, wheel_odometry_logger,
      pid_gains_tunning) — in NO launch. Keep as tools? Add entry points + docs? Remove?
- [ ] Topic chain check: imu/data → madgwick imu/out → EKF; odom → EKF → filtered;
      cmd_vel → twist_relay → controller. Stale? Duped?
- [ ] Is twist_relay even needed? Who sends raw cmd_vel (teleop? nav?)?

---

## 4. PARAMS & NODE NAMES — match or lose

- [ ] Every Node(name=...) in launch MUST match its YAML block. Rename one place = orphan params.
- [ ] use_sim_time: control.launch has it; localization/real_robot don't. Plumb it through all.
- [ ] simple_navigator defaults vs control_params.yaml — ONE source of truth.
- [ ] Hardware params (port, baud): node params or hardcoded?
- [ ] Tuning changes: log old/new/why + test link (Conventions).

---

## 5. PACKAGES — need or drop

- [ ] rosdep/colcon check vs package.xml imports.
- [ ] Suspects:
  - bringup: rplidar_ros (any lidar?), rviz2, hardware — needed?
  - localization: smbus2, i2c-tools — MPU wiring, keep?
  - description: joint_state_publisher_gui, rviz2 — dev only
- [ ] control: ros2launch declared but CMake maybe wrong type. ament_cmake_python vs setup.py?

---

## 6. LAUNCH REWRITE — goal state (best practice)

- [ ] ONE bringup entrypoint. Include package launches. No copy-paste.
- [ ] All paths PathJoinSubstitution.
- [ ] No magic timers. Events or retry-spawn.
- [ ] Nodes set on_exit behavior, consistent remaps.
- [ ] use_sim_time plumbed everywhere.
- [ ] Add sim launch (gazebo) if sim planned.

---

## 7. NODES — do they ACTUALLY work?

- [ ] Each python node vs its docstring — still true?
  - simple_navigator, go_to_goal_server, go_to_goal_client, twist_relay
  - mpu6050_driver (I2C init, rate, publishes imu/data?)
  - utils nodes
- [ ] myrobot_hardware_interface.cpp — joints/commands match controllers.yaml
      (left_wheel_joint, right_wheel_joint)?
- [ ] Firmware tune_pid.ino — serial protocol, baud 115200 — match hardware?

---

## 8. VISION — ArUco anchors (absolute pose)

Its OWN subsystem. Output = absolute pose → EKF. Kills odom drift between points.
NOT nav logic. Only makes localization truthful. (Later: markers → tasks.)

- [ ] CAMERA DRIVER: URDF has camera_link (front, −60° tilt) but NO driver.
      Add v4l2_camera/usb_cam or custom. Deps: cv_bridge + OpenCV aruco.
- [ ] INTRINSICS: checkerboard calib. Save camera_info. Accuracy = calibration quality.
- [ ] aruco_pose_anchor NODE:
  - [ ] map marker_id → known (x,y,yaw), measured once when placing markers.
  - [ ] detect + solvePnP → camera pose in marker frame.
  - [ ] static camera_link→base_footprint TF → robot pose.
  - [ ] publish PoseWithCovarianceStamped (absolute).
- [ ] GARBAGE IN: reject too-far (>2–3 m), too-oblique (bad yaw), partial.
- [ ] EKF WIRING: marker = ABSOLUTE source, tuned covariance. Nudge, don't snap.
- [ ] STRATEGY USE (decided §10): ArUco = drift-kill while driving + corner re-zero.
      Camera/anchors are REQUIRED before strategy legs; not optional.
- [ ] Test: roll past markers. Pose jumps toward truth. Between markers = dead-reckon.

---

## 9. PROXIMITY — ultrasonic stop + wall-follow (optional)

SAFETY/ASSIST only. Range = 1-D. NOT pose. NOT localization (that's Section 8).
Independent, always-on, ignores odom.

- [ ] WIRING: current stack = wheels only on /dev/ttyUSB0. Need: extend Arduino,
      new tty, or I2C/GPIO on host. Decide count+placement first (cone spread).
      URDF frames + driver node.
- [ ] OBSTACLE: stop / ease if anything within X cm ahead (behind if rear sensor).
- [ ] WALL-FOLLOW: pair of sensors → keep setpoint distance off wall,
      control on range DIFFERence. Heading relative to wall only. Not absolute.
- [ ] Test: approach wall → stops. Drive parallel → standoff holds.

---

## 10. STRATEGY SETTER — the brain (PLAN DECIDED)

> DECIDED strategy (Eurobot 2026, simple, current hardware):
> 1. Start from nest (blue or yellow side).
> 2. Go to FIRST crate stock → pick up 2 crates (gripper capacity).
> 3. Deliver them where they belong (pantry, or nest fallback).
> 4. Go to NEXT stock, pick up, deliver.
> 5. Return to nest before match end.
> 6. DRIFT CORRECTION while driving:
>    - Always checking ArUco anchors → absolute pose nudge.
>    - Near a corner / ArUco → stop, re-localize.
>    - Wall-corner bump = hard re-zero (drift kill).
> Pattern = FSM + rule table. NOT a behavior tree (plain advice-backed decision).

### ROLE / RESPONSIBILITIES (decide + write down before any code)

- [ ] WHAT it sees (inputs): current odom pose, mission/state of navigator,
      battery/safety, sensor events (vision ArUco, proximity), time.
- [ ] WHAT it decides (outputs): pick a waypoint/task, send it to the navigator
      action server (Stage 6), decide hold/next/done, emergency stop.
- [ ] HOW it talks: action client → navigate_to_pose (Stage 6). Topics for
      telemetry. Who is authoritative (strategy vs nav vs safety)?
- [ ] Failure policy: action aborted/rejected → strategy decides retry, skip,
      stop? Autonomy level (no-go zones, battery threshold)?

### MISSION MODEL (Eurobot, decided)

One match = ordered task list. Each task = waypoint + task_slot:

```
{ x, y, yaw_target, task_slot }
task_slot ∈ { PICK_2, DELIVER_PANTRY, DELIVER_NEST, RETURN_NEST, CORNER_REZERO }
```

- Mission = FSM over tasks: PICK_2 → DELIVER → next PICK_2 → DELIVER → RETURN_NEST.
- Drift correction hooks run DURING any driving leg:
  - ArUco seen → nudge pose (absolute source into EKF, §8).
  - Near corner/ArUco waypoint → hold, re-localize.
  - Corner bump → hard re-zero odom, continue.
- Deadline law: last X s reserved for RETURN_NEST (non-negotiable).
- Decision table (next PR after design doc): which crate-pick first,
  pantry vs nest fallback per zone, retry/skip on failure.

### DELIVERY PLAN

- [ ] Write design doc in docs/ (state diagram, mission = task list,
      inputs/outputs, decision table, deadline reserve).
- [ ] Skeleton node: FSM + logging, no real decisions yet.
- [ ] Wire action client to simple_navigator action server (Stage 6).
- [ ] Implement mission executor: ordered task list w/ task_slot, stop at last.
- [ ] Implement deadline law: RETURN_NEST reserve, abort current task if margin gone.
- [ ] Inject events: ArUco nudge (§8) + corner re-zero hook along drive legs.
- [ ] First real decision: PICK_2 first-pick selection by score (nearest/priority).

### HARDWARE FACTS TO CONFIRM (do before design doc)

- [ ] Gripper capacity = 2 crates (pick 2 → deliver once)? Confirm.
- [ ] Where crates live on ASR off stock area positions — map to arena coords.
- [ ] Can robot reliably bump corner wall w/o gearbox stress? Then hard re-zero.
- [ ] ArUco camera: front tilt −60° covers enough of arena? Cam driver still missing (§8).

---

## CONVENTIONS (the law)

- One task = one PR. Branch `type/CU-id-slug`. Conventional commits. Template in docs/.
- Tuning changed: document old vs new vs why + test link. NEVER silent retune.
