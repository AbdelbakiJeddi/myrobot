#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult

from myrobot_interfaces.msg import MotorFeedback

import serial
import time


class PIDTunning(Node):

    def __init__(self):

        super().__init__("pid_tunning")


        # ==========================
        # PARAMETERS
        # ==========================

        # Left PID + FF
        self.declare_parameter("left_kp", 20.0)
        self.declare_parameter("left_ki", 5.0)
        self.declare_parameter("left_kd", 0.0)
        self.declare_parameter("left_ks", 30.0)
        self.declare_parameter("left_kv", 10.0)

        # Right PID + FF
        self.declare_parameter("right_kp", 20.0)
        self.declare_parameter("right_ki", 5.0)
        self.declare_parameter("right_kd", 0.0)
        self.declare_parameter("right_ks", 30.0)
        self.declare_parameter("right_kv", 10.0)

        # Velocity command
        self.declare_parameter("left_velocity", 0.0)
        self.declare_parameter("right_velocity", 0.0)


        # Load parameters
        
        self.left_kp = self.get_parameter("left_kp").value
        self.left_ki = self.get_parameter("left_ki").value
        self.left_kd = self.get_parameter("left_kd").value
        self.left_ks = self.get_parameter("left_ks").value
        self.left_kv = self.get_parameter("left_kv").value

        self.right_kp = self.get_parameter("right_kp").value
        self.right_ki = self.get_parameter("right_ki").value
        self.right_kd = self.get_parameter("right_kd").value
        self.right_ks = self.get_parameter("right_ks").value
        self.right_kv = self.get_parameter("right_kv").value

        self.left_velocity = self.get_parameter("left_velocity").value

        self.right_velocity = self.get_parameter("right_velocity").value


        # ==========================
        # SERIAL CONNECTION
        # ==========================

        self.serial_port = "/dev/ttyUSB0"
        self.baud_rate = 115200
        self._serial_buffer = ""

        try:

            self.ser = serial.Serial(
                self.serial_port,
                self.baud_rate,
                timeout=0.0
            )

            # Arduino reset delay
            time.sleep(2)

            self.get_logger().info(
                f"Connected to {self.serial_port}"
            )


        except serial.SerialException as e:

            self.get_logger().error(
                f"Serial connection failed: {e}"
            )

            self.ser = None



        # ==========================
        # ROS INTERFACE
        # ==========================

        self.feedback_pub = self.create_publisher(
            MotorFeedback,
            "/motor_feedback",
            10
        )


        # Read serial at 100Hz
        self.serial_timer = self.create_timer(
            0.05,
            self.read_serial
        )


        # Parameter callback

        self.add_on_set_parameters_callback(
            self.parameter_callback
        )


    # ==========================
    # PARAMETER CALLBACK
    # ==========================

    def parameter_callback(self, params):

        send_left_pid = False
        send_right_pid = False
        send_velocity = False


        for param in params:


            self.get_logger().info(
                f"{param.name} changed to {param.value}"
            )


            setattr(
                self,
                param.name,
                param.value
            )


            # PID changes

            if param.name in [
                "left_kp",
                "left_ki",
                "left_kd",
                "left_ks",
                "left_kv"
            ]:

                send_left_pid = True



            elif param.name in [
                "right_kp",
                "right_ki",
                "right_kd",
                "right_ks",
                "right_kv"
            ]:

                send_right_pid = True



            elif param.name in [
                "left_velocity",
                "right_velocity"
            ]:

                send_velocity = True



        # Send updated values

        if send_left_pid:
            self.send_left_pid()


        if send_right_pid:
            self.send_right_pid()


        if send_velocity:
            self.send_velocity(
                self.left_velocity,
                self.right_velocity
            )



        return SetParametersResult(
            successful=True
        )



    # ==========================
    # SERIAL FUNCTIONS
    # ==========================


    def send_serial(self, msg):

        if self.ser is None:
            return


        if not msg.endswith("\n"):
            msg += "\n"


        self.ser.write(
            msg.encode()
        )



    def send_velocity(self,left,right):

        msg = (
            f"L:{left},R:{right}"
        )

        self.send_serial(msg)



    def send_left_pid(self):

        msg = (
            f"LP:{self.left_kp},"
            f"LI:{self.left_ki},"
            f"LD:{self.left_kd},"
            f"LKS:{self.left_ks},"
            f"LKV:{self.left_kv}"
        )

        self.send_serial(msg)



    def send_right_pid(self):

        msg = (
            f"RP:{self.right_kp},"
            f"RI:{self.right_ki},"
            f"RD:{self.right_kd},"
            f"RKS:{self.right_ks},"
            f"RKV:{self.right_kv}"
        )

        self.send_serial(msg)



    # ==========================
    # SERIAL READ
    # ==========================

    def read_serial(self):
        if self.ser is None:
            return
        
        self.send_velocity(self.left_velocity,self.right_velocity)

        try:
            if self.ser.in_waiting == 0:
                return

            raw = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="replace")
            self._serial_buffer += raw
        except Exception as e:
            self.get_logger().error(f"Serial read error: {e}")
            return

        # Process complete lines only
        while "\n" in self._serial_buffer:
            line, self._serial_buffer = self._serial_buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue

            if not (line.startswith("L:") and ",R:" in line):
                self.get_logger().warning(f"Discarding malformed line: {line}")
                continue

            try:
                left_part, right_part = line.split(",R:", 1)
                left_vals = left_part.replace("L:", "").split(",")
                right_vals = right_part.split(",")

                if len(left_vals) != 3 or len(right_vals) != 3:
                    raise ValueError("Wrong field count")

                msg = MotorFeedback()
                msg.left_ticks    = int(left_vals[0])
                msg.left_velocity = float(left_vals[1])
                msg.left_pwm      = float(left_vals[2])
                msg.right_ticks   = int(right_vals[0])
                msg.right_velocity= float(right_vals[1])
                msg.right_pwm     = float(right_vals[2])

                self.feedback_pub.publish(msg)

            except Exception as e:
                self.get_logger().error(f"Parse error on '{line}': {e}")



def main(args=None):
    rclpy.init(args=args)
    node = PIDTunning()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()



if __name__ == "__main__":
    main()