/*
 * Dual-motor feedforward calibration for myrobot.
 *
 * Sweeps PWM from MIN_PWM to 255 on BOTH motors simultaneously, measures the
 * steady-state wheel velocity from each encoder, and prints a CSV you can
 * paste into analyze_ff.py to get per-wheel kS/kV gains.
 *
 * IMPORTANT: the robot must be RAISED OFF THE GROUND (wheels free-spinning) so
 * the measured velocity is the no-load wheel speed. Loaded (on-floor) gains
 * will differ slightly; re-run on the floor afterwards for final tuning.
 *
 * Wiring (must match robot_control.ino):
 *   RIGHT: enA=10, in1=7, in2=8,  encA=3, encB=4
 *   LEFT : enB=9,  in3=6, in4=5,  encA=2, encB=A1
 */

#include <Arduino.h>
#include <math.h>

// ---- RIGHT motor (L298N side A) ----
#define R_EN  10
#define R_IN1 7
#define R_IN2 8
#define R_ENC_A 3
#define R_ENC_B 4

// ---- LEFT motor (L298N side B) ----
#define L_EN  9
#define L_IN3 6
#define L_IN4 5
#define L_ENC_A 2
#define L_ENC_B A1

#define PPR        225
#define WINDOW_MS  50      // velocity averaging window
#define SETTLE_MS  2000    // wait for speed to stabilize
#define PWM_STEP   10
#define MIN_PWM    30

volatile unsigned long r_count = 0;
volatile unsigned long l_count = 0;
volatile bool r_sign = true;
volatile bool l_sign = true;

void rIsr() { r_sign = (digitalRead(R_ENC_B) == HIGH); r_count++; }
void lIsr() { l_sign = (digitalRead(L_ENC_B) != HIGH); l_count++; }

float measureRight() {
  noInterrupts(); unsigned long c = r_count; r_count = 0; interrupts();
  return (2.0 * M_PI * c * 1000.0) / (PPR * WINDOW_MS);
}
float measureLeft() {
  noInterrupts(); unsigned long c = l_count; l_count = 0; interrupts();
  return (2.0 * M_PI * c * 1000.0) / (PPR * WINDOW_MS);
}

void setRight(int pwm) {
  digitalWrite(R_IN1, HIGH); digitalWrite(R_IN2, LOW);
  analogWrite(R_EN, pwm);
}
void setLeft(int pwm) {
  digitalWrite(L_IN3, HIGH); digitalWrite(L_IN4, LOW);
  analogWrite(L_EN, pwm);
}

void driveBoth(int pwm) { setRight(pwm); setLeft(pwm); }

void setup() {
  Serial.begin(115200);
  pinMode(R_EN, OUTPUT); pinMode(R_IN1, OUTPUT); pinMode(R_IN2, OUTPUT);
  pinMode(L_EN, OUTPUT); pinMode(L_IN3, OUTPUT); pinMode(L_IN4, OUTPUT);
  pinMode(R_ENC_A, INPUT); pinMode(R_ENC_B, INPUT);
  pinMode(L_ENC_A, INPUT); pinMode(L_ENC_B, INPUT);
  attachInterrupt(digitalPinToInterrupt(R_ENC_A), rIsr, RISING);
  attachInterrupt(digitalPinToInterrupt(L_ENC_A), lIsr, RISING);
  driveBoth(0);
  delay(500);

  Serial.println("pwm,r_vel,l_vel");
  for (int pwm = MIN_PWM; pwm <= 255; pwm += PWM_STEP) {
    driveBoth(pwm);
    delay(SETTLE_MS);
    // average 5 windows
    float rs = 0, ls = 0;
    for (int i = 0; i < 5; i++) { rs += measureRight(); ls += measureLeft(); }
    rs /= 5.0; ls /= 5.0;
    Serial.print(pwm); Serial.print(",");
    Serial.print(rs, 4); Serial.print(",");
    Serial.println(ls, 4);
  }
  driveBoth(0);
  Serial.println("# done");
}

void loop() {}
