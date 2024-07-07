import sys
import serial
import struct
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

class FootSoleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Foot Sole Sensor Visualization")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.foot_sole_widget = FootSoleWidget()
        layout.addWidget(self.foot_sole_widget)

        self.ser = serial.Serial('/dev/ttyUSB0', baudrate=460800, timeout=0.001)
        self.buffer = bytearray()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10)  # Update every 10 ms

    def update_data(self):
        if self.ser.in_waiting:
            self.buffer.extend(self.ser.read(self.ser.in_waiting))
            
            while len(self.buffer) >= 216:
                packet = self.buffer[:216]
                self.buffer = self.buffer[216:]

                frame_head, frame_type, frame_length, package_type, *sensor_values, checksum = struct.unpack('<HBHB208BH', packet)

                if frame_head == 0x5Aa5 and frame_type == 0x01 and frame_length == 0x00D6 and package_type == 0x01:
                    calculated_checksum = sum(packet[:-2]) & 0xFFFF
                    if calculated_checksum == checksum:
                        self.foot_sole_widget.update_values(sensor_values)
                    else:
                        print(f"Checksum error. Calculated: {calculated_checksum:04X}, Received: {checksum:04X}")
                else:
                    print(f"Invalid packet structure. Head: {frame_head:04X}, Type: {frame_type:02X}, Length: {frame_length:04X}, Package: {package_type:02X}")

    def closeEvent(self, event):
        self.ser.close()
        super().closeEvent(event)

class FootSoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.values = [0] * 208

    def update_values(self, new_values):
        self.values = new_values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        cell_width = self.width() / 13
        cell_height = self.height() / 16

        for row in range(16):
            for col in range(13):
                index = row * 13 + col
                value = self.values[index]
                color = QColor(255, 255 - value, 255 - value)  # Red intensity based on value
                painter.fillRect(col * cell_width, row * cell_height, cell_width, cell_height, color)
                painter.drawRect(col * cell_width, row * cell_height, cell_width, cell_height)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = FootSoleGUI()
    gui.show()
    sys.exit(app.exec_())
