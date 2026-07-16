/*
 * PID step-response logger for myrobot wheel velocity control.
 *
 * Holds the robot still, then commands a step in wheel velocity and logs the
 * measured velocity of BOTH wheels over time so you can tune Kp/Ki by eye
 * (or with plot_step.py). Run, open the Serial Plotter / monitor at 115200,
 * copy the lines (they start with "t,") into a CSV, then:
 *
 *     python3 plot_step.py step.csv
 *
 * The robot should be RAISED OFF THE GROUND for this test.
 *
 * Wiring matches robot_control.ino.
 */

#include <Arduino.h>
#include <math.h>
#include <PID_v1.h>

#define R_EN 10
#define R_IN1 7
#define R_IN2 8
#define R_ENC_A 3
#define R_ENC_B 4
#define L_EN 9
#define L_IN3 6
#define L_IN4 5
#define L_ENC_A 2
#define L_ENC_B A1

#define PPR 225
#define WINDOW_MS 10

volatile unsigned long r_count = 0, l_count = 0;
volatile bool r_sign = true, l_sign = true;
void rIsr() { r_sign = (digitalRead(R_ENC_B) == HIGH); r_count++; }
void lIsr() { l_sign = (digitalRead(L_ENC_B) != HIGH); l_count++; }

double r_meas = 0, l_meas = 0;
double r_cmd_vel = 0, l_cmd_vel = 0;
double r_pwm = 0, l_pwm = 0;

double kS_r = 0.0, kV_r = 4.34;
double kS_l = 0.0, kV_l = 4.74;
double Kp = 2.0, Ki = 3.0, Kd = 0.0;

PID rPid(&r_meas, &r_pwm, &r_cmd_vel, Kp, Ki, Kd, DIRECT);
PID lPid(&l_meas, &l_pwm, &l_cmd_vel, Kp, Ki, Kd, DIRECT);

float measR() { noInterrupts(); unsigned long c = r_count; r_count = 0; interrupts();
  return (2.0 * M_PI * c * 1000.0) / (PPR * WINDOW_MS); }
float measL() { noInterrupts(); unsigned long c = l_count; l_count = 0; interrupts();
  return (2.0 * M_PI * c * 1000.0) / (PPR * WINDOW_MS); }

void drive(int rp, int lp) {
  digitalWrite(R_IN1, HIGH); digitalWrite(R_IN2, LOW); analogWrite(R_EN, rp);
  digitalWrite(L_IN3, HIGH); digitalWrite(L_IN4, LOW); analogWrite(L_EN, lp);
}

unsigned long t0;
const double STEP_VEL = 10.0;   // rad/s step command
const unsigned long HOLD_BEFORE = 2000;
const unsigned long HOLD_AFTER = 4000;
bool started = false;

void setup() {
  Serial.begin(115200);
  pinMode(R_EN, OUTPUT); pinMode(R_IN1, OUTPUT); pinMode(R_IN2, OUTPUT);
  pinMode(L_EN, OUTPUT); pinMode(L_IN3, OUTPUT); pinMode(L_IN4, OUTPUT);
  pinMode(R_ENC_A, INPUT); pinMode(R_ENC_B, INPUT);
  pinMode(L_ENC_A, INPUT); pinMode(L_ENC_B, INPUT);
  attachInterrupt(digitalPinToInterrupt(R_ENC_A), rIsr, RISING);
  attachInterrupt(digitalPinToInterrupt(L_ENC_A), lIsr, RISING);
  rPid.SetMode(AUTOMATIC); lPid.SetMode(AUTOMATIC);
  rPid.SetOutputLimits(0, 255); lPid.SetOutputLimits(0, 255);
  drive(0, 0);
  delay(500);
  Serial.println("t,r_vel,l_vel,r_pwm,l_pwm"); // CSV header
  t0 = millis();
}

void loop() {
  unsigned long t = millis() - t0;
  if (t >= HOLD_BEFORE && t <= HOLD_BEFORE + HOLD_AFTER) {
    r_cmd_vel = STEP_VEL; l_cmd_vel = STEP_VEL;
  } else {
    r_cmd_vel = 0; l_cmd_vel = 0;
  }

  r_meas = measR(); l_meas = measL();
  rPid.Compute(); lPid.Compute();

  double rff = (r_cmd_vel != 0.0) ? (max(0.0, kS_r) + kV_r * fabs(r_cmd_vel)) : 0.0;
  double lff = (l_cmd_vel != 0.0) ? (max(0.0, kS_l) + kV_l * fabs(l_cmd_vel)) : 0.0;
  int rp = (r_cmd_vel == 0.0) ? 0 : constrain((int)(r_pwm + rff), 0, 255);
  int lp = (l_cmd_vel == 0.0) ? 0 : constrain((int)(l_pwm + lff), 0, 255);
  drive(rp, lp);

  Serial.print(t); Serial.print(",");
  Serial.print(r_meas, 3); Serial.print(",");
  Serial.print(l_meas, 3); Serial.print(",");
  Serial.print(rp); Serial.print(",");
  Serial.println(lp);

  delay(WINDOW_MS);
}
