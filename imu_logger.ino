#include <helper_3dmath.h>
#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include <MPU6050.h>
#include <Wire.h>

MPU6050 mpu;

bool SIM = false;

void setup() {
  Serial.begin(115200);

  Wire.begin();
  mpu.initialize();
  // Possible values: 250, 500, 1000, 2000 (°/s)
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_1000);  // Less sensitive than default (250)
  // Possible values: 2, 4, 8, 16 (g)
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_16);  // Less sensitive than default (2g)
  if (mpu.testConnection()) {
    Serial.println("MPU6050 connected.");
  } else {
    Serial.println("MPU6050 connection failed.");
  }
}

void loop() {
  if (SIM) {
    /// Time-based variable to simulate smooth changes
    unsigned long t = millis();

    // Simulate smooth tilt (in raw units ~ ±16384 = ±1g)
    float tiltAmplitude = 4000; // adjust for more/less tilt
    int16_t ax = tiltAmplitude * sin(t / 1000.0);
    int16_t ay = tiltAmplitude * sin(t / 1500.0 + 1);
    int16_t az = 16384 + tiltAmplitude * sin(t / 2000.0 + 2); // mostly gravity

    // Simulate small gyro movements (degrees per second)
    float gyroAmplitude = 50; // gentle rotation
    int16_t gx = gyroAmplitude * sin(t / 900.0);
    int16_t gy = gyroAmplitude * sin(t / 1100.0 + 1);
    int16_t gz = gyroAmplitude * sin(t / 1300.0 + 2);

    // Output as CSV
    Serial.print(ax); Serial.print(",");
    Serial.print(ay); Serial.print(",");
    Serial.print(az); Serial.print(",");
    Serial.print(gx); Serial.print(",");
    Serial.print(gy); Serial.print(",");
    Serial.println(gz);

    delay(5); // 200 Hz
    return; // Skip the real sensor reading
  }

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 disconnected. Attempting to reconnect...");
    Wire.begin();
    mpu.initialize();
    delay(1000); // Give some time to reconnect
    return; // Skip this loop iteration
  }

  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);

  delay(5); // 200 Hz
}