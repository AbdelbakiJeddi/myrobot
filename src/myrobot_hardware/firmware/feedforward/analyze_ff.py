#!/usr/bin/env python3
"""
Analyze feedforward calibration CSVs and print kS/kV gains.

Usage:
    python3 analyze_ff.py r-ff.txt l-ff.txt

The CSV format is two columns: pwm,vel (rad/s). Lines starting with '#'
or 'pwm,vel' are ignored. The rising, linear region (default pwm 40-140)
is fitted as vel = slope*pwm + intercept, then inverted to:

    pwm = kS + kV * vel

where  kS = -intercept/slope   (static threshold, ~0 for these motors)
        kV = 1/slope           (velocity gain)
"""
import sys
import numpy as np


def load(fn):
    xs, ys = [], []
    with open(fn) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or line == 'pwm,vel' or not line:
                continue
            p, v = line.split(',')
            xs.append(float(p))
            ys.append(float(v))
    return np.array(xs), np.array(ys)


def fit(p, v, lo=40, hi=140):
    mask = (p >= lo) & (p <= hi)
    slope, intercept = np.polyfit(p[mask], v[mask], 1)
    kV = 1.0 / slope
    kS = -intercept / slope
    return kS, kV, slope, intercept


def report(name, fn):
    p, v = load(fn)
    kS, kV, slope, intercept = fit(p, v)
    print(f"{name}:")
    print(f"  fit region pwm [{p.min():.0f},{p.max():.0f}], used [{40},{140}]")
    print(f"  vel = {slope:.5f}*pwm + {intercept:.3f}")
    print(f"  => kS = {kS:.2f}   kV = {kV:.3f}")
    print(f"  copy into robot_control.ino:")
    print(f"    double kS_{name.lower()} = {kS:.2f}; double kV_{name.lower()} = {kV:.3f};")
    print()
    return kS, kV


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for arg in sys.argv[1:]:
        report(arg.split('/')[-1].replace('-ff.txt', '').upper(), arg)
