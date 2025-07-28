# IMU Visualizer

A real-time desktop application for visualizing orientation and sensor data from an MPU6050 IMU using Python, PyQt5, and Matplotlib.

## Features

- **Live 3D Orientation Viewer**  
  Displays sensor orientation via 3D arrows and a cube that rotates with pitch, roll, and yaw.

- **Sensor Readout Display**  
  Realtime labels for accelerometer (ax, ay, az), gyroscope (gx, gy, gz), and derived orientation angles.

- **CSV Logging System**  
  Press "Start" to begin recording a flight, and "Export CSV" to save a timestamped log of the session.

- **Serial Connection Diagnostics**  
  Automatically detects the connected IMU device, displays the connection status and port.

- **Robust Parsing + Reconnect Logic**  
  Detects malformed or dropped lines and provides graceful error handling without crashing.

- **Modular Architecture**  
  Codebase is split into well-structured components:
  - `SerialHandler`: Reads and parses serial data
  - `Logger`: Handles log buffering and CSV export
  - `OrientationUtils`: Calculates pitch, roll, yaw
  - `Render3D`: Handles all 3D visualization logic
  - `IMUVisualizer`: Manages UI and data flow

## Getting Started

### Requirements

- Python 3.7+
- PyQt5
- matplotlib
- numpy
- scipy
- pyserial

Install with pip:

```bash
pip install pyqt5 matplotlib numpy scipy pyserial
```
