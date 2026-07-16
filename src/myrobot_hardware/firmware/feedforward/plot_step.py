#!/usr/bin/env python3
"""
Plot a PID step-response CSV captured from tune_pid.ino.

Usage:
    python3 plot_step.py step.csv

Expected CSV columns: t,r_vel,l_vel,r_pwm,l_pwm
Plots wheel velocities and PWM for both wheels so you can judge overshoot,
settling time, and (crucially) whether LEFT and RIGHT track together.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) < 2:
        print("usage: python3 plot_step.py step.csv")
        sys.exit(1)
    fn = sys.argv[1]
    data = np.genfromtxt(fn, delimiter=",", names=True, dtype=None, encoding=None)
    t = data["t"] / 1000.0  # ms -> s

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

    ax1.plot(t, data["r_vel"], label="right vel (rad/s)")
    ax1.plot(t, data["l_vel"], label="left vel (rad/s)")
    ax1.axhline(10.0, color="k", ls="--", lw=0.8, label="step target")
    ax1.set_ylabel("wheel velocity (rad/s)")
    ax1.set_title("PID step response — both wheels should overlap")
    ax1.legend()
    ax1.grid(True)

    ax2.plot(t, data["r_pwm"], label="right pwm")
    ax2.plot(t, data["l_pwm"], label="left pwm")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("PWM (0-255)")
    ax2.legend()
    ax2.grid(True)

    out = fn.rsplit(".", 1)[0] + "_step.png"
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print(f"saved plot to {out}")


if __name__ == "__main__":
    main()
