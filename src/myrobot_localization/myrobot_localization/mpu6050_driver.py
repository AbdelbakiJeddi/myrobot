#!/usr/bin/env python3
"""
MPU6050 ROS 2 driver node.

Ported from the Arduino Mpu6050.h header-only library.
Features mirrored from the Arduino version:
  - Proper sensor configuration (wake, 1 kHz sample rate, DLPF band 3 @ 44 Hz)
  - Startup calibration for both accelerometer and gyroscope (500 samples each)
  - Offset subtraction on every read (accel Z compensated for 1 g)
  - 14-byte burst read (accel + temp + gyro) for consistency
"""

import rclpy
import rclpy.time
import smbus2
import math
import time
import struct
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu

# ── MPU-6050 register map ────────────────────────────────────────────────────
DEVICE_ADDRESS = 0x68
REG_PWR_MGMT_1 = 0x6B
REG_SMPLRT_DIV = 0x19
REG_CONFIG     = 0x1A
REG_GYRO_CONFIG  = 0x1B
REG_ACCEL_CONFIG = 0x1C
REG_INT_ENABLE   = 0x38
REG_ACCEL_XOUT_H = 0x3B      # first byte of the 14-byte burst


ACCEL_SCALE = 16384.0          
GYRO_SCALE  = 131.0            
ONE_G_LSB   = 16384            

DLPF_CFG = 3

CALIBRATION_SAMPLES = 1000
CALIBRATION_DELAY   = 0.005


class MPU6050_Driver(Node):

    def __init__(self):
        super().__init__("mpu6050_driver")

        self.acc_off_x = 0
        self.acc_off_y = 0
        self.acc_off_z = 0
        self.gyro_off_x = 0
        self.gyro_off_y = 0
        self.gyro_off_z = 0

        self.is_connected_ = False
        self.bus_ = None
        self.read_error_count_ = 0
        self.MAX_READ_ERRORS = 5
        self.init_mpu6050(calibrate=True)

        self.imu_pub_ = self.create_publisher(
            Imu, "/imu/data_raw", qos_profile=qos_profile_sensor_data
        )
        self.imu_msg_ = Imu()
        self.imu_msg_.header.frame_id = "imu_link"

        # Orientation: not provided (MPU6050 has no magnetometer)
        # covariance[0] = -1 tells downstream nodes to ignore orientation
        self.imu_msg_.orientation_covariance[0] = -1.0

        # Angular velocity covariance (diagonal, in rad²/s²)
        # MPU6050 gyro noise density: 0.005 °/s/√Hz
        # At DLPF 44 Hz: σ ≈ 0.005 × √44 × π/180 ≈ 5.8e-4 rad/s → σ² ≈ 3.4e-7
        # Using 1e-6 with margin for real-world conditions
        self.imu_msg_.angular_velocity_covariance[0] = 1e-6  # xx
        self.imu_msg_.angular_velocity_covariance[4] = 1e-6  # yy
        self.imu_msg_.angular_velocity_covariance[8] = 1e-6  # zz

        # Linear acceleration covariance (diagonal, in m²/s⁴)
        # MPU6050 accel noise density: 400 µg/√Hz
        # At DLPF 44 Hz: σ ≈ 400e-6 × √44 × 9.81 ≈ 0.026 m/s² → σ² ≈ 6.8e-4
        # Using 1e-3 with margin for real-world conditions
        self.imu_msg_.linear_acceleration_covariance[0] = 1e-3  # xx
        self.imu_msg_.linear_acceleration_covariance[4] = 1e-3  # yy
        self.imu_msg_.linear_acceleration_covariance[8] = 1e-3  # zz

        self.period_ = 0.01  # 100 Hz
        self.timer_ = self.create_timer(self.period_, self.timer_callback)

    def init_mpu6050(self, calibrate=False):
        try:
            # 1. Prevent resource leaking: Close the old bus handle if it exists
            if self.bus_ is not None:
                try:
                    self.bus_.close()
                except Exception:
                    pass  # Quietly fail if it was already closed or dead
                self.bus_ = None

            # 2. Open a fresh connection file descriptor
            self.bus_ = smbus2.SMBus(1)

            # Wake up the MPU6050 (comes out of sleep mode)
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_PWR_MGMT_1, 0x00)
            time.sleep(0.1)

            # Sample-rate divider: SampleRate = 1 kHz / (1 + DIV)
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_SMPLRT_DIV, 0x00)

            # Set DLPF (Digital Low-Pass Filter) configuration
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_CONFIG, DLPF_CFG)

            # Gyro full scale range (±250°/s)
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_GYRO_CONFIG, 0x00)

            # Accel full scale range (±2g)
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_ACCEL_CONFIG, 0x00)

            # Enable data-ready interrupt
            self.bus_.write_byte_data(DEVICE_ADDRESS, REG_INT_ENABLE, 0x01)

            # Mark as connected BEFORE calibration so read_raw_burst() works
            self.is_connected_ = True

            if calibrate:
                self.get_logger().info("MPU-6050 initialised — running calibration…")
                self.calibrate()
                self.get_logger().info("MPU-6050 calibration complete and ready.")
            else:
                self.get_logger().info("MPU-6050 reconnected — registers restored, offsets preserved.")
            
        except OSError as e:
            self.is_connected_ = False
            self.get_logger().error(f"MPU-6050 init failed: {e}")

    def calibrate(self):
        self.calibrate_accel()
        self.calibrate_gyro()

    def calibrate_accel(self):
        sx, sy, sz = 0, 0, 0
        valid_samples = 0
        while valid_samples < CALIBRATION_SAMPLES:
            raw = self.read_raw_burst()
            if raw is not None:
                sx += raw[0]
                sy += raw[1]
                sz += raw[2]
                valid_samples += 1
            time.sleep(CALIBRATION_DELAY)

        self.acc_off_x = int(sx / CALIBRATION_SAMPLES)
        self.acc_off_y = int(sy / CALIBRATION_SAMPLES)
        self.acc_off_z = int(sz / CALIBRATION_SAMPLES) - ONE_G_LSB

    def calibrate_gyro(self):
        sx, sy, sz = 0, 0, 0
        valid_samples = 0
        while valid_samples < CALIBRATION_SAMPLES:
            raw = self.read_raw_burst()
            if raw is not None:
                sx += raw[3]
                sy += raw[4]
                sz += raw[5]
                valid_samples += 1
            time.sleep(CALIBRATION_DELAY)

        self.gyro_off_x = int(sx / CALIBRATION_SAMPLES)
        self.gyro_off_y = int(sy / CALIBRATION_SAMPLES)
        self.gyro_off_z = int(sz / CALIBRATION_SAMPLES)

    def read_raw_burst(self):
        """
        Burst-read 14 bytes starting at ACCEL_XOUT_H:
            AX_H AX_L  AY_H AY_L  AZ_H AZ_L  T_H T_L  GX_H GX_L  GY_H GY_L  GZ_H GZ_L
        Returns (ax, ay, az, gx, gy, gz) as signed 16-bit integers, or None on error.
        Temperature word is skipped (matches Arduino code).
        """
        try:
            data = self.bus_.read_i2c_block_data(DEVICE_ADDRESS, REG_ACCEL_XOUT_H, 14)
            vals = struct.unpack(">hhhhhhh", bytes(data))
            return (vals[0], vals[1], vals[2], vals[4], vals[5], vals[6])
        except OSError:
            return None


    def timer_callback(self):
        try:
            if not self.is_connected_:
                self.init_mpu6050(calibrate=False)
                return

            raw = self.read_raw_burst()
            if raw is None:
                self.read_error_count_ += 1
                if self.read_error_count_ >= self.MAX_READ_ERRORS:
                    self.get_logger().warn("Too many I2C read failures — reconnecting…")
                    self.is_connected_ = False
                    self.read_error_count_ = 0
                return

            self.read_error_count_ = 0

            ax = raw[0] - self.acc_off_x
            ay = raw[1] - self.acc_off_y
            az = raw[2] - self.acc_off_z
            gx = raw[3] - self.gyro_off_x
            gy = raw[4] - self.gyro_off_y
            gz = raw[5] - self.gyro_off_z

            self.imu_msg_.linear_acceleration.x = (ax / ACCEL_SCALE) * 9.80665
            self.imu_msg_.linear_acceleration.y = (ay / ACCEL_SCALE) * 9.80665
            self.imu_msg_.linear_acceleration.z = (az / ACCEL_SCALE) * 9.80665
            self.imu_msg_.angular_velocity.x = (gx / GYRO_SCALE) * (math.pi / 180.0)
            self.imu_msg_.angular_velocity.y = (gy / GYRO_SCALE) * (math.pi / 180.0)
            self.imu_msg_.angular_velocity.z = (gz / GYRO_SCALE) * (math.pi / 180.0)

            self.imu_msg_.header.stamp = self.get_clock().now().to_msg()
            self.imu_pub_.publish(self.imu_msg_)

        except OSError:
            self.is_connected_ = False


def main():
    rclpy.init()
    mpu6050_driver = MPU6050_Driver()
    rclpy.spin(mpu6050_driver)
    mpu6050_driver.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()