import sys
import colorsys
import serial
import struct
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

SENSOR_LAYOUT = [
    [0, 0, 0, 0, 0, 201, 202, 203, 204, 205, 206, 0, 0],
    [0, 0, 0, 0, 200, 0, 0, 0, 0, 0, 0, 207, 0],
    [0, 0, 0, 199, 0, 0, 0, 0, 0, 0, 0, 0, 208],
    [0, 0, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [79, 80, 81, 82, 83, 84, 85, 86, 87, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 67, 68, 69, 70, 71, 72, 73, 74, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 54, 55, 56, 57, 58, 59, 60, 61, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 49, 0, 0, 0],
    [0, 0, 42, 43, 44, 45, 46, 47, 48, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 0, 0, 0],
    [0, 0, 29, 30, 31, 32, 33, 34, 35, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 17, 18, 19, 20, 21, 22, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 6, 7, 8, 9, 0, 0, 0, 0],
]

class FootSoleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Foot Sole Sensor Visualization")
        self.setGeometry(100, 100, 650, 1000)

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
        self.sensor_mapping = {sensor_id: i for i, row in enumerate(SENSOR_LAYOUT) for sensor_id in row if sensor_id != 0}
        self.min_value = 0
        self.max_value = 255  # Assuming 8-bit sensor values

    def update_values(self, new_values):
        self.values = new_values
        self.min_value = min(self.values)
        self.max_value = max(self.values)
        self.update()

    def value_to_color(self, value):
        if self.max_value == self.min_value:
            hue = 0
        else:
            hue = (1 - (value - self.min_value) / (self.max_value - self.min_value)) * 0.7
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        return QColor.fromRgbF(rgb[0], rgb[1], rgb[2])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        cell_width = width // 13
        cell_height = height // 32

        # Define the square dimensions
        square_size = min(cell_width, cell_height) * 0.8  # Make it 80% of the smaller cell dimension

        # Set up font for displaying values
        font = QFont()
        font.setPointSize(8)  # Adjust font size as needed
        painter.setFont(font)

        for row, row_data in enumerate(SENSOR_LAYOUT):
            for col, sensor_id in enumerate(row_data):
                if sensor_id != 0:
                    x = col * cell_width
                    y = row * cell_height
                    
                    # Center the square in the cell
                    square_x = x + (cell_width - square_size) / 2
                    square_y = y + (cell_height - square_size) / 2
                    
                    value = self.values[sensor_id - 1]  # Adjust for 0-based indexing
                    color = self.value_to_color(value)
                    painter.setBrush(color)
                    painter.setPen(QPen(Qt.black, 1))
                    painter.drawRect(square_x, square_y, square_size, square_size)

                    # Display non-zero values
                    if value > 0:
                        # Choose text color based on background brightness
                        if color.lightness() > 128:
                            painter.setPen(Qt.black)
                        else:
                            painter.setPen(Qt.white)
                        painter.drawText(square_x, square_y, square_size, square_size, 
                                         Qt.AlignCenter, str(value))
                                         
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = FootSoleGUI()
    gui.show()
    sys.exit(app.exec_())
