import sys
import serial
import numpy as np
import math
import csv
import time

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
        self.logging_active = False
        self.log = []  # List of rows to write

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

        # Set up 3d model dimensions
        self.cube_vertices = np.array([
            [-1, -1, -1],
            [ 1, -1, -1],
            [ 1,  1, -1],
            [-1,  1, -1],
            [-1, -1,  1],
            [ 1, -1,  1],
            [ 1,  1,  1],
            [-1,  1,  1]
        ]) * 4  # Scale cube size

        self.cube_faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [1, 2, 6, 5],
            [0, 3, 7, 4]
        ]

        self.rendered_cube_patches = []

        self.status_label = QLabel('<b>Status:</b> <span style="color:Tomato;">Disconnected</span>')
        self.timestamp_label = QLabel("Last update: ---")

        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')

        self.export_button = QPushButton('Export Data as CSV')
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.export_log)

        # Orientation + sensor data labels
        self.pitch_label = QLabel("Pitch: ---")
        self.roll_label = QLabel("Roll: ---")
        self.yaw_label = QLabel("Yaw: ---")

        self.ax_label = QLabel("ax: ---")
        self.ay_label = QLabel("ay: ---")
        self.az_label = QLabel("az: ---")

        self.gx_label = QLabel("gx: ---")
        self.gy_label = QLabel("gy: ---")
        self.gz_label = QLabel("gz: ---")

        layout = QVBoxLayout()

        layout.addWidget(self.status_label)
        layout.addWidget(self.timestamp_label)
        layout.addWidget(self.export_button)

        layout.addWidget(self.canvas)

        data_layout = QGridLayout()
        data_layout.addWidget(self.pitch_label, 0, 0)
        data_layout.addWidget(self.roll_label, 0, 1)
        data_layout.addWidget(self.yaw_label, 0, 2)

        data_layout.addWidget(self.ax_label, 1, 0)
        data_layout.addWidget(self.ay_label, 1, 1)
        data_layout.addWidget(self.az_label, 1, 2)

        data_layout.addWidget(self.gx_label, 2, 0)
        data_layout.addWidget(self.gy_label, 2, 1)
        data_layout.addWidget(self.gz_label, 2, 2)

        layout.addLayout(data_layout)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_serial)
        self.stop_button.clicked.connect(self.stop_serial)


    def start_serial(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.timer.start(int(self.dt * 1000))
            self.start_time = time.time()
            self.flight_log = []
            self.logging_active = True
            self.export_button.setEnabled(False)
            self.status_label.setText(f'<b>Status:</b> <span style="color:MediumSeaGreen;">Connected to {self.ser.port} | Logging: Active</span>')
        except Exception as e:
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Failed to connect ({e})</span>')

    def stop_serial(self):
        self.timer.stop()
        if self.ser:
            self.ser.close()
        self.logging_active = False
        self.status_label.setText(f'<b>Status:</b> <span style="color:DodgerBlue;"> Disconnected from {self.ser.port} | Logging Stopped</span>')
        self.export_button.setEnabled(True)

    def export_log(self):
        try:
            with open('imu_log.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'pitch', 'roll', 'yaw'])
                writer.writerows(self.log)
            self.status_label.setText('<b>Status:</b> <span style="color:MediumSeaGreen;">Data exported to imu_log.csv</span>')
            self.export_button.setEnabled(False)
        except Exception as e:
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Export failed ({e})</span>')

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
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Disconnected ({e})</span>')
            return

        try:
            line = self.ser.readline().decode('utf-8').strip()
            if not line: return
            parts = list(map(int, line.split(',')))
            if len(parts) != 6:
                return
            ax, ay, az = parts[0], parts[1], parts[2]
            gx, gy, gz = parts[3], parts[4], parts[5]

            self.timestamp_label.setText(f"Last update: {time.strftime('%H:%M:%S')}")
            
            pitch, roll, yaw = self.compute_orientation(ax, ay, az, gz)

            self.pitch_label.setText(f"Pitch: {pitch:.2f}")
            self.roll_label.setText(f"Roll: {roll:.2f}")
            self.yaw_label.setText(f"Yaw: {yaw:.2f}")

            self.ax_label.setText(f"ax: {ax}")
            self.ay_label.setText(f"ay: {ay}")
            self.az_label.setText(f"az: {az}")

            self.gx_label.setText(f"gx: {gx}")
            self.gy_label.setText(f"gy: {gy}")
            self.gz_label.setText(f"gz: {gz}")
            
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

            # Apply rotation to cube vertices
            rotated_vertices = rotation.apply(self.cube_vertices)

            # Remove previously drawn cube faces
            for patch in self.rendered_cube_patches:
                patch.remove()
            self.rendered_cube_patches.clear()
            
            for face_indices in self.cube_faces:
                face_coords = [rotated_vertices[i] for i in face_indices]
                poly = Poly3DCollection([face_coords], facecolor='#CD7F32', edgecolor='k', alpha=0.4)
                self.ax.add_collection3d(poly)
                self.rendered_cube_patches.append(poly)

            self.canvas.draw()

            if self.logging_active:
                timestamp = round((time.time() - self.start_time) * 1000)
                self.log.append([timestamp, ax, ay, az, gx, gy, gz, pitch, roll, yaw])
        except Exception as e:
            print(f"Parse error: {e}")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    vis = IMUVisualizer()
    vis.resize(600, 600)
    vis.show()
    sys.exit(app.exec_())