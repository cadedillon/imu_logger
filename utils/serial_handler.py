import serial

# --- Serial config ---
SERIAL_PORT = '/dev/tty.usbmodemB081849903302'
BAUD_RATE = 115200

class SerialHandler:
    def __init__(self):
        self.ser = None
        self.port = SERIAL_PORT

    def start_serial(self):
        self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    def stop_serial(self):
        if self.ser:
            self.ser.close()



        