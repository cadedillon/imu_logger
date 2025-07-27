import math

class OrientationUtils:
    def __init__(self, timer=None, dt=0.005):
          self.yaw = 0.0
          self.timer = timer
          self.prev_time = None
          self.dt = dt

    def compute_orientation(self, ax, ay, az, gz):
        try:
            current_time = self.timer.remainingTime() / 1000.0 if self.prev_time is None else self.dt

            # Convert raw gyroscope value to deg/sec
            gyro_scale = 1 # Assuming raw gz is in degrees per second
            gz_dps = gz / gyro_scale
            self.yaw += gz_dps * current_time  # integrate over time

            # Wrap yaw to [0, 360)
            self.yaw = (self.yaw + 360) % 360

            self.prev_time = self.dt

            pitch = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
            roll  = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2)))
        except ZeroDivisionError:
            pitch, roll = 0.0, 0.0
        return pitch, roll, self.yaw