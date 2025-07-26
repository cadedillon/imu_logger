import sys
import serial
import numpy as np
import math

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtCore import QTimer

from scipy.spatial.transform import Rotation as R


# --- Serial config ---
SERIAL_PORT = '/dev/tty.usbmodemB081849903302'
BAUD_RATE = 115200

class IMUVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IMU Visualizer')
        self.ser = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.dt = 0.005  # 200hz
        self.yaw = 0.0
        self.prev_time = None

        # --- UI setup ---
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        self.ax.set_xlim([-20, 20])
        self.ax.set_ylim([-20, 20])
        self.ax.set_zlim([-20, 20])
        self.ax.set_xlabel('X (forward)')
        self.ax.set_ylabel('Y (left)')
        self.ax.set_zlabel('Z (up)')

        # Initialize quiver arrows with dummy directions
        self.x_arrow = self.ax.quiver(0, 0, 0, 1, 0, 0, color='r', length=20, normalize=True)
        self.y_arrow = self.ax.quiver(0, 0, 0, 0, 1, 0, color='g', length=20, normalize=True)
        self.z_arrow = self.ax.quiver(0, 0, 0, 0, 0, 1, color='b', length=20, normalize=True)


        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_serial)
        self.stop_button.clicked.connect(self.stop_serial)


    def start_serial(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.timer.start(int(self.dt * 1000))
        except Exception as e:
            print(f"Serial error: {e}")

    def stop_serial(self):
        self.timer.stop()
        if self.ser:
            self.ser.close()

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


    def update_plot(self):
        if not self.ser or not self.ser.in_waiting:
            return

        try:
            line = self.ser.readline().decode('utf-8').strip()
            if not line: return
            parts = list(map(int, line.split(',')))
            if len(parts) != 6:
                return
            ax, ay, az = parts[0], parts[1], parts[2]
            gz = parts[5]
            
            pitch, roll, yaw = self.compute_orientation(ax, ay, az, gz)
            print(f"Pitch: {pitch:.2f}, Roll: {roll:.2f}, Yaw: {yaw:.2f}")
            
            # Convert angles to rotation
            rotation = R.from_euler('xyz', [math.radians(pitch), math.radians(roll), math.radians(yaw)])
            x_axis = rotation.apply([1, 0, 0])  # forward
            y_axis = rotation.apply([0, 1, 0])  # left
            z_axis = rotation.apply([0, 0, 1])  # up

            # Update quiver arrow directions
            self.x_arrow.remove()
            self.y_arrow.remove()
            self.z_arrow.remove()

            self.x_arrow = self.ax.quiver(0, 0, 0, x_axis[0], x_axis[1], x_axis[2], color='r', length=20, normalize=True)
            self.y_arrow = self.ax.quiver(0, 0, 0, y_axis[0], y_axis[1], y_axis[2], color='g', length=20, normalize=True)
            self.z_arrow = self.ax.quiver(0, 0, 0, z_axis[0], z_axis[1], z_axis[2], color='b', length=20, normalize=True)

            self.canvas.draw()
        except Exception as e:
            print(f"Parse error: {e}")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    vis = IMUVisualizer()
    vis.resize(600, 600)
    vis.show()
    sys.exit(app.exec_())