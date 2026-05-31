#include <Arduino.h>
#include <math.h>

#define L298N_enA   10
#define L298N_in1   8
#define L298N_in2   7
#define ENC_A       3
#define ENC_B       4

#define PPR           225
#define INTERVAL      50      // ms per velocity window
#define SETTLE_MS     2000    // wait after each PWM change
#define PWM_STEP      10

volatile unsigned long pulse_count = 0;
void encoderISR() { pulse_count++; }

float measure_vel() {
  noInterrupts(); pulse_count = 0; interrupts();
  delay(INTERVAL);
  noInterrupts(); unsigned long c = pulse_count; interrupts();
  return (2.0 * M_PI * c * 1000.0) / (PPR * INTERVAL);
}

void setup() {
  Serial.begin(115200);
  pinMode(L298N_enA, OUTPUT);
  pinMode(L298N_in1, OUTPUT);
  pinMode(L298N_in2, OUTPUT);
  digitalWrite(L298N_in1, HIGH);
  digitalWrite(L298N_in2, LOW);
  analogWrite(L298N_enA, 0);
  pinMode(ENC_A, INPUT);
  pinMode(ENC_B, INPUT);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, RISING);

  Serial.println("pwm,vel");   // CSV header for plotting

  for (int pwm =30; pwm <= 255; pwm += PWM_STEP) {
    analogWrite(L298N_enA, pwm);
    delay(SETTLE_MS);          // let velocity stabilize

    // average 5 windows
    float sum = 0;
    for (int i = 0; i < 5; i++) sum += measure_vel();
    float vel = sum / 5.0;

    Serial.print(pwm);
    Serial.print(",");
    Serial.println(vel, 4);
  }

  analogWrite(L298N_enA, 0);
  Serial.println("# done");
}

void loop() {}
