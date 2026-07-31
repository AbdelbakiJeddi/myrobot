#include <PID_v1.h>
#include <Arduino.h>
#include <Encoder.h>
#include <math.h>

// ================= MOTOR DRIVER PINS =================

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
const double TICKS_PER_REV = 450.0; // Adjust to match your hardware encoder resolution

// Timing settings
const unsigned long CONTROL_INTERVAL_MS = 20; // 50 Hz PID control loop
const unsigned long FEEDBACK_INTERVAL_MS = 20; // Feedback rate (50 Hz matches control loop)
const unsigned long CMD_TIMEOUT_MS = 500;     // Safety watchdog timeout (0.5 seconds)

long lastLeftTicks = 0;
long lastRightTicks = 0;
long currentLeftTicks = 0;
long currentRightTicks = 0;

unsigned long last_control_time = 0;
unsigned long last_feedback_time = 0;
unsigned long last_command_time = 0;

// Velocity setpoints and feedback (rad/s)
double left_target_vel = 0.0;
double right_target_vel = 0.0;

// Velocity filter parameter (Exponential Moving Average)
// alpha = 1.0 (unfiltered), alpha = 0.2-0.4 (smooth low-pass filtering)
const double VELOCITY_FILTER_ALPHA = 0.35;

double left_measured_vel = 0.0;
double right_measured_vel = 0.0;

// Motor PWM outputs (-255 to 255)
double left_pwm = 0.0;
double right_pwm = 0.0;

// ================= FEEDFORWARD GAINS =================
// kS: Voltage/PWM offset needed to overcome static friction (stiction)
// kV: Voltage/PWM per unit velocity (rad/s)
double kS_l = 10.0;
double kV_l = 20.0;

double kS_r = 10.0;
double kV_r = 20.0;

// ================= PID GAINS =================
double Kp_l = 20.0;
double Ki_l = 5.0;
double Kd_l = 0.0;

double Kp_r = 20.0;
double Ki_r = 5.0;
double Kd_r = 0.0;

// PID controllers
PID leftPID(&left_measured_vel, &left_pwm, &left_target_vel, Kp_l, Ki_l, Kd_l, DIRECT);
PID rightPID(&right_measured_vel, &right_pwm, &right_target_vel, Kp_r, Ki_r, Kd_r, DIRECT);

// Forward declarations
void readCommand();
void calculateVelocity(double dt);
void setRightMotor(double pwm);
void setLeftMotor(double pwm);
void stopMotors();
void sendFeedback();

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

  leftPID.SetMode(AUTOMATIC);
  rightPID.SetMode(AUTOMATIC);

  // Set limits for feedback PID component
  leftPID.SetOutputLimits(-255, 255);
  rightPID.SetOutputLimits(-255, 255);

  unsigned long now = millis();
  last_control_time = now;
  last_feedback_time = now;
  last_command_time = now;
}

// ================= MAIN LOOP =================

void loop()
{
  readCommand();

  unsigned long now = millis();

  // Watchdog: Stop motors if command stream stops
  if (now - last_command_time > CMD_TIMEOUT_MS)
  {
    left_target_vel = 0.0;
    right_target_vel = 0.0;
  }

  // 50Hz Control Calculation Loop
  if (now - last_control_time >= CONTROL_INTERVAL_MS)
  {
    double dt = (now - last_control_time) / 1000.0;
    last_control_time = now;

    calculateVelocity(dt);

    // Run feedback PID computation
    leftPID.Compute();
    rightPID.Compute();

    // Calculate feedforward terms: FF = kS * sign(v) + kV * v
    double left_ff = 0.0;
    double right_ff = 0.0;

    if (abs(left_target_vel) > 0.001)
    {
      left_ff = (left_target_vel > 0 ? kS_l : -kS_l) + (kV_l * left_target_vel);
    }

    if (abs(right_target_vel) > 0.001)
    {
      right_ff = (right_target_vel > 0 ? kS_r : -kS_r) + (kV_r * right_target_vel);
    }

    // Combine PID feedback and feedforward
    double total_left_pwm = left_pwm + left_ff;
    double total_right_pwm = right_pwm + right_ff;

    // Clean stop when setpoint is zero
    if (abs(left_target_vel) < 0.001)
    {
      total_left_pwm = 0.0;
      left_pwm = 0.0;
    }
    if (abs(right_target_vel) < 0.001)
    {
      total_right_pwm = 0.0;
      right_pwm = 0.0;
    }

    // Constrain PWM output within hardware range
    total_left_pwm = constrain(total_left_pwm, -255.0, 255.0);
    total_right_pwm = constrain(total_right_pwm, -255.0, 255.0);

    setLeftMotor(total_left_pwm);
    setRightMotor(total_right_pwm);
  }

  // Send encoder and velocity feedback to host
  if (now - last_feedback_time >= FEEDBACK_INTERVAL_MS)
  {
    sendFeedback();
    last_feedback_time = now;
  }
}

// ================= HELPER FUNCTIONS =================

void calculateVelocity(double dt)
{
  if (dt <= 0.0001) return;

  currentLeftTicks = leftEncoder.read();
  currentRightTicks = rightEncoder.read();

  long dLeft = currentLeftTicks - lastLeftTicks;
  long dRight = currentRightTicks - lastRightTicks;

  lastLeftTicks = currentLeftTicks;
  lastRightTicks = currentRightTicks;

  double leftTPS = (double)dLeft / dt;
  double rightTPS = (double)dRight / dt;

  double left_vel_raw = leftTPS * 2.0 * M_PI / TICKS_PER_REV;
  double right_vel_raw = rightTPS * 2.0 * M_PI / TICKS_PER_REV;

  // Exponential Moving Average (EMA) low-pass filter
  left_measured_vel = VELOCITY_FILTER_ALPHA * left_vel_raw + (1.0 - VELOCITY_FILTER_ALPHA) * left_measured_vel;
  right_measured_vel = VELOCITY_FILTER_ALPHA * right_vel_raw + (1.0 - VELOCITY_FILTER_ALPHA) * right_measured_vel;
}

void readCommand()
{
  static char buffer[64];
  static byte idx = 0;

  while (Serial.available() > 0)
  {
    char c = Serial.read();
    if (c == '\n' || c == '\r')
    {
      if (idx > 0)
      {
        buffer[idx] = '\0';
        float L, R;
        if (sscanf(buffer, "L:%f,R:%f", &L, &R) == 2)
        {
          left_target_vel = L;
          right_target_vel = R;
          last_command_time = millis();
        }
        idx = 0;
      }
    }
    else if (idx < sizeof(buffer) - 1)
    {
      buffer[idx++] = c;
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
  analogWrite(L298N_enA, abs((int)pwm));
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
  analogWrite(L298N_enB, abs((int)pwm));
}

void stopMotors()
{
  analogWrite(L298N_enA, 0);
  analogWrite(L298N_enB, 0);
}

void sendFeedback()
{
  // Output format matches host driver expecting: "L:<ticks>,<vel>,R:<ticks>,<vel>\n"
  Serial.print("L:");
  Serial.print(currentLeftTicks);
  Serial.print(",");
  Serial.print(left_measured_vel, 3);

  Serial.print(",R:");
  Serial.print(currentRightTicks);
  Serial.print(",");
  Serial.print(right_measured_vel, 3);

  Serial.print("\n");
}