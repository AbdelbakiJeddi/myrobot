#include <PID_v1.h>
#include <Arduino.h>
#include <Encoder.h>
#include <math.h>

// ================= MOTOR DRIVER =================

#define L298N_enA 10
#define L298N_enB 9

#define L298N_in4 5
#define L298N_in3 6
#define L298N_in2 8
#define L298N_in1 7

// ================= ENCODERS =================

Encoder leftEncoder(2, A1);
Encoder rightEncoder(3, 4);

// Encoder parameters
const double TICKS_PER_REV = 450.0; // CHANGE to your encoder

long lastLeftTicks = 0;
long lastRightTicks = 0;

unsigned long last_millis = 0;
const unsigned long interval = 20; // 50Hz

double left_target_vel = 0;
double right_target_vel = 0;

double left_measured_vel = 0;
double right_measured_vel = 0;

double left_pwm = 0;
double right_pwm = 0;

// PID gains

double Kp_r = 20;
double Ki_r = 5;
double Kd_r = 0;

double Kp_l = 20;
double Ki_l = 5;
double Kd_l = 0;

// PID controllers

PID rightPID(&right_measured_vel, &right_pwm, &right_target_vel, Kp_r, Ki_r, Kd_r, DIRECT);

PID leftPID(&left_measured_vel, &left_pwm, &left_target_vel, Kp_l, Ki_l, Kd_l, DIRECT);

// ================= SETUP =================

void setup()
{
  Serial.begin(115200);

  pinMode(L298N_enA, OUTPUT);
  pinMode(L298N_enB, OUTPUT);

  pinMode(L298N_in1, OUTPUT);
  pinMode(L298N_in2, OUTPUT);
  pinMode(L298N_in3, OUTPUT);
  pinMode(L298N_in4, OUTPUT);

  stopMotors();

  rightPID.SetMode(AUTOMATIC);
  leftPID.SetMode(AUTOMATIC);

  // allow forward/backward
  rightPID.SetOutputLimits(-255, 255);
  leftPID.SetOutputLimits(-255, 255);

  last_millis = millis();
}

void loop()
{

  readCommand();

  unsigned long now = millis();

  if (now - last_millis >= interval)
  {
    calculateVelocity();
    rightPID.Compute();
    leftPID.Compute();
    setRightMotor(right_pwm);
    setLeftMotor(left_pwm);
    last_millis = now;
  }

  // send feedback
  if (millis() - last_feedback_time >= FEEDBACK_INTERVAL_MS)
  {
    sendFeedback();
    last_feedback_time = millis();
  }

}

void calculateVelocity()
{

  long leftTicks = leftEncoder.read();
  long rightTicks = rightEncoder.read();

  long dLeft = leftTicks - lastLeftTicks;
  long dRight = rightTicks - lastRightTicks;

  lastLeftTicks = leftTicks;
  lastRightTicks = rightTicks;

  double dt = interval / 1000.0;

  double leftTPS = dLeft / dt;
  double rightTPS = dRight / dt;

  left_measured_vel =
      leftTPS * 2.0 * M_PI / TICKS_PER_REV;

  right_measured_vel =
      rightTPS * 2.0 * M_PI / TICKS_PER_REV;
}


void readCommand()
{
  if (Serial.available())
  {
    String line = Serial.readStringUntil('\n');
    float L, R;
    if (sscanf(line.c_str(), "L:%f,R:%f", &L, &R) == 2)
    {
      left_target_vel = L;
      right_target_vel = R;
    }
  }
}

void setRightMotor(double pwm)
{
  if (pwm >= 0)
  {
    digitalWrite(L298N_in1, HIGH);
    digitalWrite(L298N_in2, LOW);
  }
  else
  {
    digitalWrite(L298N_in1, LOW);
    digitalWrite(L298N_in2, HIGH);
  }
  analogWrite(L298N_enA, abs(pwm));
}

void setLeftMotor(double pwm)
{
  if (pwm >= 0)
  {
    digitalWrite(L298N_in3, HIGH);
    digitalWrite(L298N_in4, LOW);
  }
  else
  {
    digitalWrite(L298N_in3, LOW);
    digitalWrite(L298N_in4, HIGH);
  }
  analogWrite(L298N_enB, abs(pwm));
}

void stopMotors()
{
  analogWrite(L298N_enA, 0);
  analogWrite(L298N_enB, 0);
}

void sendFeedback()
{
  Serial.print("L:");
  Serial.print(left_encoder_ticks);
  Serial.print(",");
  Serial.print(left_measured_velocity, 3);

  Serial.print(",R:");
  Serial.print(right_encoder_ticks);
  Serial.print(",");
  Serial.print(right_measured_velocity, 3);

  Serial.print("\n");
}