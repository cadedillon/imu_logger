from PyQt5.QtWidgets import QApplication
from widgets.visualizer import IMUVisualizer
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vis = IMUVisualizer()
    vis.resize(600, 600)
    vis.show()
    sys.exit(app.exec_())