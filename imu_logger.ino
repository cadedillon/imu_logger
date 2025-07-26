#include <helper_3dmath.h>
#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include <MPU6050.h>
#include <Wire.h>

MPU6050 mpu;

void setup() {
  Serial.begin(9600);

  Wire.begin();
  mpu.initialize();
  if (mpu.testConnection()) {
    Serial.println("MPU6050 connected.");
  } else {
    Serial.println("MPU6050 connection failed.");
  }
}

void loop() {
  // Simulated accelerometer and gyro values
  int16_t ax = random(-10, 11);
  int16_t ay = random(-10, 11);
  int16_t az = random(-10, 11);
  int16_t gx = random(-10, 11);
  int16_t gy = random(-10, 11);
  int16_t gz = random(-10, 11);

  // Output as CSV
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);

  delay(100); // 10 Hz
}