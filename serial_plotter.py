import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Open serial port 
ser = serial.Serial('/dev/tty.usbmodemB081849903302', 9600)

data = {'gx': [], 'gy': [], 'gz': []}
max_points = 100

def update(frame):
    line = ser.readline().decode('utf-8').strip()
    try:
        _, _, _, gx, gy, gz = map(int, line.split(","))
        data['gx'].append(gx)
        data['gy'].append(gy)
        data['gz'].append(gz)

        print(data)
        
        # Keep only the last N points
        for k in data:
            if len(data[k]) > max_points:
                data[k] = data[k][-max_points:]
        
        ax.clear()
        ax.plot(data['gx'], label='gx')
        ax.plot(data['gy'], label='gy')
        ax.plot(data['gz'], label='gz')
        ax.legend(loc='upper right')
        ax.set_ylim(-15, 15)
        ax.set_xlim(-15, 15)
    except ValueError:
        pass  # Ignore malformed lines

fig, ax = plt.subplots()
ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()