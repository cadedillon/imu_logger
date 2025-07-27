import time
import csv

class Logger:
    def __init__(self, filename, timer=None):
        self.filename = filename
        self.logging_active = False
        self.log = []  # List of rows to write
        self.timer = timer
        self.start_time = None

    def start_logging(self):
        self.log = []
        self.logging_active = True
        self.start_time = time.time()

    def log_data(self, ax, ay, az, gx, gy, gz, pitch, roll, yaw):
        if self.logging_active:
                timestamp = round((time.time() - self.start_time) * 1000)
                self.log.append([timestamp, ax, ay, az, gx, gy, gz, pitch, roll, yaw])

    def stop_logging(self):
        self.logging_active = False

    def export_log(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'pitch', 'roll', 'yaw'])
            writer.writerows(self.log)
        