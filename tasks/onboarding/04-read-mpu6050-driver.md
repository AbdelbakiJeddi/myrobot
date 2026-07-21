# Task: Read and Explain `mpu6050_driver.py`

## Description
Read `src/myrobot_localization/myrobot_localization/mpu6050_driver.py` end to end. Write a short doc explaining: the I2C bus (`smbus2`), the MPU6050 register map at the top of the file, the wake + DLPF + sample-rate setup, the calibration routine, the 14-byte burst read, and the published `sensor_msgs/Imu` message. This node publishes the IMU topic the EKF consumes. Reading it teaches the full IMU pipeline.

## Desired Output
- New file `tasks/onboarding/mpu6050_driver_explained.md`.
- Sections: registers, init flow, calibration, burst read, message publish, covariances, reconnection on error.
- One-line summary at the top: "mpu6050_driver talks to the MPU6050 over I2C, calibrates it on startup, and publishes `/imu/out` for the EKF."

## Input
- `src/myrobot_localization/myrobot_localization/mpu6050_driver.py`.
- `src/myrobot_localization/config/ekf.yaml` (line 13: `imu0: /imu/out`).

## Configuration
- No code change. Read-only task.

## Docs Needed
- [ ] `tasks/onboarding/mpu6050_driver_explained.md`.
