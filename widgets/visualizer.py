import time

# Library imports
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import QTimer

# Application imports
from widgets.render3d import Render3D
from orientation_utils import OrientationUtils
from logger import Logger
from serial_handler import SerialHandler

class IMUVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IMU Visualizer')
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.dt = 0.005  # 200hz

        # --- UI setup ---
        self.canvas = Render3D(self)

        # --- Utilities setup ---
        self.serial = SerialHandler()
        self.logger = Logger("./data/imu_log.csv", timer=self.timer)
        self.orientation = OrientationUtils(timer=self.timer, dt=self.dt)
        
        # --- UI elements ---
        # Connection status and timestamp
        self.status_label = QLabel('<b>Status:</b> <span style="color:Tomato;">Disconnected</span>')
        self.timestamp_label = QLabel("Last update: ---")
        
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

        # Buttons for start/stop and export
        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')
        self.export_button = QPushButton('Export Data as CSV')

        # Button functionality
        self.start_button.clicked.connect(self.start)
        self.stop_button.clicked.connect(self.stop)
        self.export_button.clicked.connect(self.export)
        self.export_button.setEnabled(False)


        # --- UI layout ---
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

    def start(self):
        try:
            self.serial.start_serial()
            self.logger.start_logging()
            self.timer.start(int(self.dt * 1000))
            self.export_button.setEnabled(False)
            self.status_label.setText(f'<b>Status:</b> <span style="color:MediumSeaGreen;">Connected to {self.serial.port} | Logging: Active</span>')
        except Exception as e:
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Failed to connect ({e})</span>')  
    
    def stop(self):
        self.timer.stop()
        self.serial.stop_serial()
        self.logger.stop_logging()
        self.status_label.setText(f'<b>Status:</b> <span style="color:DodgerBlue;"> Disconnected from {self.serial.port} | Logging Stopped</span>')
        self.export_button.setEnabled(True)
    
    def export(self):
        try:
            self.logger.export_log()
            self.status_label.setText('<b>Status:</b> <span style="color:MediumSeaGreen;">Data exported to data/imu_log.csv</span>')
            self.export_button.setEnabled(False)
        except Exception as e:
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Export failed ({e})</span>')

    def updateDataReadout(self, pitch, roll, yaw, ax, ay, az, gx, gy, gz):
            self.timestamp_label.setText(f"Last update: {time.strftime('%H:%M:%S')}")

            # Derived values
            self.pitch_label.setText(f"Pitch: {pitch:.2f}")
            self.roll_label.setText(f"Roll: {roll:.2f}")
            self.yaw_label.setText(f"Yaw: {yaw:.2f}")

            # Accelerometer values
            self.ax_label.setText(f"ax: {ax}")
            self.ay_label.setText(f"ay: {ay}")
            self.az_label.setText(f"az: {az}")

            # Gyroscope values
            self.gx_label.setText(f"gx: {gx}")
            self.gy_label.setText(f"gy: {gy}")
            self.gz_label.setText(f"gz: {gz}")

    def update_plot(self):
        try:
            line = self.serial.ser.readline().decode('utf-8').strip()
            if not line: return
            parts = list(map(int, line.split(',')))
            if len(parts) != 6:
                return
            ax, ay, az = parts[0], parts[1], parts[2]
            gx, gy, gz = parts[3], parts[4], parts[5]

            # compute new orientation
            pitch, roll, yaw = self.orientation.compute_orientation(ax, ay, az, gz)
            
            # Update the 3D visualization
            self.canvas.update_orientation(pitch, roll, yaw)

            # Update log
            self.logger.log_data(ax, ay, az, gx, gy, gz, pitch, roll, yaw)

            # Update data readout
            self.updateDataReadout(pitch, roll, yaw, ax, ay, az, gx, gy, gz)

        except Exception as e:
            self.status_label.setText(f'<b>Status:</b> <span style="color:Tomato;">Error: ({e})</span>')
            print(f"Parse error: {e}")
