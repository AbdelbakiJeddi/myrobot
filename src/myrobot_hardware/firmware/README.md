# Firmware — motor control & tuning

## Files
- `robot_control/robot_control.ino` — main firmware flashed to the Arduino. Talks to the
  ROS 2 `myrobot_hardware` ros2_control plugin over serial (`r<sign><vel>,l<sign><vel>,`).
  Per-wheel PI velocity control with feedforward: `pwm = PI_output + max(0,kS) + kV*|cmd_vel|`.
- `feedforward/calibrate.ino` — raises the robot off the ground, sweeps PWM 30→255 on **both**
  motors, prints `pwm,r_vel,l_vel` CSV. Use to (re)measure feedforward gains.
- `feedforward/analyze_ff.py` — fits `kS`/`kV` per wheel from the CSV above.
- `feedforward/tune_pid.ino` — step-response logger for tuning Kp/Ki.
- `feedforward/plot_step.py` — plots the step response; checks left/right track together.
- `feedforward/r-ff.txt`, `l-ff.txt` — previous no-load sweep data (reference).

## Tuning workflow (do this on real hardware)
1. **Raise the robot** so wheels spin freely.
2. Flash `calibrate.ino`, open Serial Monitor @115200, copy the `pwm,r_vel,l_vel` lines to
   `sweep.csv`.
3. `python3 analyze_ff.py sweep.csv` → paste the printed `kS_*`/`kV_*` into `robot_control.ino`.
4. Flash `robot_control.ino`. Drive straight; if it still veers, the remaining error is
   tracking — tune Kp/Ki:
   - Flash `tune_pid.ino`, capture the `t,r_vel,l_vel,...` lines to `step.csv`.
   - `python3 plot_step.py step.csv`. Left and right velocity traces must overlap.
   - If overshoot/oscillation: lower Kp. If slow to reach target / steady offset: raise Ki.
   - Keep Kp_r==Kp_l and Ki_r==Ki_l; rely on feedforward for the per-wheel difference.
5. (Optional) Repeat step 1–3 **on the floor** (loaded) for final gains.

## Why both wheels need their own gains
The motors/gears/wheels are not identical. A single shared `kS`/`kV` forces the PI loop to
absorb the difference, which it cannot do symmetrically → the robot curves. Calibrate each
wheel independently.
