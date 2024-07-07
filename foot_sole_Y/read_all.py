import serial
import struct
import time
import sys

def read_sensor_data():
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=460800,
        timeout=0.001  # Reduced timeout
    )
    buffer = bytearray()
    packet_size = 216
    update_interval = 0.1  # Update screen every 0.1 seconds
    last_update = time.time()

    try:
        while True:
            if ser.in_waiting:
                buffer.extend(ser.read(ser.in_waiting))
                
                while len(buffer) >= packet_size:
                    packet = buffer[:packet_size]
                    buffer = buffer[packet_size:]

                    frame_head, frame_type, frame_length, package_type, *sensor_values, checksum = struct.unpack('<HBHB208BH', packet)

                    if frame_head == 0x5Aa5 and frame_type == 0x01 and frame_length == 0x00D6 and package_type == 0x01:
                        calculated_checksum = sum(packet[:-2]) & 0xFFFF
                        if calculated_checksum == checksum:
                            current_time = time.time()
                            if current_time - last_update >= update_interval:
                                sys.stdout.write("\033[2J\033[H")  # Clear screen and move cursor to top-left
                                print("Data received correctly. Sensor values:")
                                for row in range(15, -1, -1):
                                    for col in range(13):
                                        index = (15 - row) * 13 + col
                                        value = sensor_values[index]
                                        sys.stdout.write(f"C{col:2d}R{row:2d}: {value:3d}  ")
                                    sys.stdout.write("\n")
                                sys.stdout.flush()
                                last_update = current_time
                        else:
                            print(f"Checksum error. Calculated: {calculated_checksum:04X}, Received: {checksum:04X}")
                    else:
                        print(f"Invalid packet structure. Head: {frame_head:04X}, Type: {frame_type:02X}, Length: {frame_length:04X}, Package: {package_type:02X}")

            time.sleep(0.001)  # Small sleep to prevent CPU hogging

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        ser.close()

if __name__ == "__main__":
    read_sensor_data()
