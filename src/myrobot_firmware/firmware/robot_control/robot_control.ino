#include <PID_v1.h>
#include <Arduino.h>
#include <math.h>

// L298N H-Bridge Connection PINs
#define L298N_enA 10 // PWM
#define L298N_enB 9  // PWM
#define L298N_in4 5  // Left Motor B
#define L298N_in3 6  // Left Motor B
#define L298N_in2 8  // Right Motor A
#define L298N_in1 7  // Right Motor A

// Wheel Encoders Connection PINs
#define right_encoder_phaseA 3  // Interrupt
#define right_encoder_phaseB 4
#define left_encoder_phaseA 2   // Interrupt
#define left_encoder_phaseB A1

// Encoders - ADDED 'volatile' because these change inside ISRs
volatile unsigned int right_encoder_counter = 0;
volatile unsigned int left_encoder_counter = 0;

String right_wheel_sign = "p";  // 'p' = positive, 'n' = negative
String left_wheel_sign = "p";  // 'p' = positive, 'n' = negative
unsigned long last_millis = 0;
const unsigned long interval = 10;  // 100Hz update rate

// Interpret Serial Messages
bool is_right_wheel_cmd = false;
bool is_left_wheel_cmd = false;
bool is_right_wheel_forward = true;
bool is_left_wheel_forward = true;
char value[] = "00.00";
uint8_t value_idx = 0;
bool is_cmd_complete = false;

// PID
double right_wheel_cmd_vel = 0.0;     // rad/s
double left_wheel_cmd_vel = 0.0;      // rad/s
double right_wheel_meas_vel = 0.0;    // rad/s
double left_wheel_meas_vel = 0.0;     // rad/s
double right_wheel_cmd = 0.0;         // 0-255
double left_wheel_cmd = 0.0;          // 0-255

// Feedforward
double kS_r = 32.0; double kV_r = 2;
double kS_l = 32.0; double kV_l = 2;

// Tuning parameters
double Kp_r = 11.0; double Ki_r = 5.0; double Kd_r = 0.0;
double Kp_l = 11.0; double Ki_l = 5.5; double Kd_l = 0.0;

PID rightMotor(&right_wheel_meas_vel, &right_wheel_cmd, &right_wheel_cmd_vel, Kp_r, Ki_r, Kd_r, DIRECT);
PID leftMotor(&left_wheel_meas_vel, &left_wheel_cmd, &left_wheel_cmd_vel, Kp_l, Ki_l, Kd_l, DIRECT);

void setup() {
  pinMode(L298N_enA, OUTPUT); pinMode(L298N_enB, OUTPUT);
  pinMode(L298N_in1, OUTPUT); pinMode(L298N_in2, OUTPUT);
  pinMode(L298N_in3, OUTPUT); pinMode(L298N_in4, OUTPUT);

  // Set Motor Rotation Direction
  digitalWrite(L298N_in1, HIGH); digitalWrite(L298N_in2, LOW);
  digitalWrite(L298N_in3, HIGH); digitalWrite(L298N_in4, LOW);

  rightMotor.SetMode(AUTOMATIC);
  leftMotor.SetMode(AUTOMATIC);
  rightMotor.SetOutputLimits(0, 150);
  leftMotor.SetOutputLimits(0, 150);
  
  Serial.begin(115200);

  pinMode(right_encoder_phaseB, INPUT);
  pinMode(left_encoder_phaseB, INPUT);
  
  attachInterrupt(digitalPinToInterrupt(right_encoder_phaseA), rightEncoderCallback, RISING);
  attachInterrupt(digitalPinToInterrupt(left_encoder_phaseA), leftEncoderCallback, RISING);
}

void loop() {
  // Read and Interpret Wheel Velocity Commands
  while (Serial.available())
  {
    char chr = Serial.read();
    
    // Explicitly ignore newline and carriage return configurations so they don't corrupt the buffer
    if (chr == '\n' || chr == '\r') {
      continue; 
    }

    if(chr == 'r')
    {
      is_right_wheel_cmd = true;
      is_left_wheel_cmd = false;
      value_idx = 0;
      is_cmd_complete = false;
    }
    else if(chr == 'l')
    {
      is_right_wheel_cmd = false;
      is_left_wheel_cmd = true;
      value_idx = 0;
    }
    else if(chr == 'p')
    {
      if(is_right_wheel_cmd && !is_right_wheel_forward)
      {
        digitalWrite(L298N_in1, HIGH - digitalRead(L298N_in1));
        digitalWrite(L298N_in2, HIGH - digitalRead(L298N_in2));
        is_right_wheel_forward = true;
      }
      else if(is_left_wheel_cmd && !is_left_wheel_forward)
      {
        digitalWrite(L298N_in3, HIGH - digitalRead(L298N_in3));
        digitalWrite(L298N_in4, HIGH - digitalRead(L298N_in4));
        is_left_wheel_forward = true;
      }
    }
    else if(chr == 'n')
    {
      if(is_right_wheel_cmd && is_right_wheel_forward)
      {
        digitalWrite(L298N_in1, HIGH - digitalRead(L298N_in1));
        digitalWrite(L298N_in2, HIGH - digitalRead(L298N_in2));
        is_right_wheel_forward = false;
      }
      else if(is_left_wheel_cmd && is_left_wheel_forward)
      {
        digitalWrite(L298N_in3, HIGH - digitalRead(L298N_in3));
        digitalWrite(L298N_in4, HIGH - digitalRead(L298N_in4));
        is_left_wheel_forward = false;
      }
    }
    else if(chr == ',')
    {
      if(is_right_wheel_cmd)
      {
        right_wheel_cmd_vel = atof(value);
      }
      else if(is_left_wheel_cmd)
      {
        left_wheel_cmd_vel = atof(value);
        is_cmd_complete = true;
      }
      // Reset for next command
      value_idx = 0;
      value[0] = '0'; value[1] = '0'; value[2] = '.'; value[3] = '0'; value[4] = '0'; value[5] = '\0';
    }
    else
    {
      if(value_idx < 5)
      {
        value[value_idx] = chr;
        value_idx++;
      }
    }
  }

  // Timed Execution Block
  unsigned long current_millis = millis();
  if(current_millis - last_millis >= interval)
  {
    // --- ATOMIC READING OF ENCODERS (Prevents Race Conditions) ---
    noInterrupts();
    unsigned int right_counter_copy = right_encoder_counter;
    unsigned int left_counter_copy = left_encoder_counter;
    right_encoder_counter = 0;
    left_encoder_counter = 0;
    interrupts();
    // -------------------------------------------------------------

    right_wheel_meas_vel = (2.0 * M_PI * right_counter_copy * 1000.0) / (225.0 * interval);
    left_wheel_meas_vel = (2.0 * M_PI * left_counter_copy * 1000.0) / (225.0 * interval);

    rightMotor.Compute();
    leftMotor.Compute();

    double right_ff = (right_wheel_cmd_vel != 0.0) ? (kS_r + kV_r * fabs(right_wheel_cmd_vel)) : 0.0;
    double left_ff = (left_wheel_cmd_vel != 0.0) ? (kS_l + kV_l * fabs(left_wheel_cmd_vel)) : 0.0;

    double right_cmd = constrain(right_wheel_cmd + right_ff, 0.0, 255.0);
    double left_cmd = constrain(left_wheel_cmd + left_ff, 0.0, 255.0);

    if(right_wheel_cmd_vel == 0.0) right_cmd = 0.0;
    if(left_wheel_cmd_vel == 0.0) left_cmd = 0.0;

    // Send payload safely back to ROS 2 (ends with explicit newline)
    Serial.print("r");
    Serial.print(right_wheel_sign);
    Serial.print(right_wheel_meas_vel);
    Serial.print(",l");
    Serial.print(left_wheel_sign);
    Serial.print(left_wheel_meas_vel);
    Serial.println(","); 

    last_millis = current_millis;

    analogWrite(L298N_enA, right_cmd);
    analogWrite(L298N_enB, left_cmd);
  }
}

void rightEncoderCallback() {
  right_wheel_sign = (digitalRead(right_encoder_phaseB) == HIGH) ? "p" : "n";
  right_encoder_counter++;
}

void leftEncoderCallback() {
  left_wheel_sign = (digitalRead(left_encoder_phaseB) == HIGH) ? "n" : "p";
  left_encoder_counter++;
}