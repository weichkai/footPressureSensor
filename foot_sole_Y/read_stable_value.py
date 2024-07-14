import serial
import struct
import time
import sys
from datetime import datetime
from collections import deque


def read_sensor_data():
    ser = serial.Serial(
        port='COM6',
        baudrate=460800,
        timeout=0.001
    )
    buffer = bytearray()
    packet_size = 216
    update_interval = 0.1
    last_update = time.time()

    # For stable value detection
    value_history = deque(maxlen=8)
    stable_value = None
    stable_value_count = 0

    try:
        while True:
            if ser.in_waiting:
                buffer.extend(ser.read(ser.in_waiting))

                while len(buffer) >= packet_size:
                    packet = buffer[:packet_size]
                    buffer = buffer[packet_size:]

                    frame_head, frame_type, frame_length, package_type, *sensor_values, checksum = struct.unpack(
                        '<HBHB208BH', packet)

                    if frame_head == 0x5Aa5 and frame_type == 0x01 and frame_length == 0x00D6 and package_type == 0x01:
                        calculated_checksum = sum(packet[:-2]) & 0xFFFF
                        if calculated_checksum == checksum:
                            current_time = time.time()
                            if current_time - last_update >= update_interval:
                                # Calculate index for C5R7
                                index = (15 - 7) * 13 + 5
                                value = sensor_values[index]
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                # Check for stable value
                                value_history.append(value)
                                is_stable = len(value_history) == 8 and len(set(value_history)) == 1

                                if is_stable and (stable_value is None or value != stable_value):
                                    stable_value_count += 1
                                    stable_value = value
                                    log_entry = f"{timestamp} - C5R7: {value} - STABLE VALUE {stable_value_count}\n"
                                else:
                                    log_entry = f"{timestamp} - C5R7: {value}\n"

                                # Append to file
                                with open('value_log.txt', 'a') as f:
                                    f.write(log_entry)

                                print(log_entry.strip())
                                sys.stdout.flush()
                                last_update = current_time
                        else:
                            print(f"Checksum error. Calculated: {calculated_checksum:04X}, Received: {checksum:04X}")
                    else:
                        print(
                            f"Invalid packet structure. Head: {frame_head:04X}, Type: {frame_type:02X}, Length: {frame_length:04X}, Package: {package_type:02X}")

            time.sleep(0.001)  # Small sleep to prevent CPU hogging

    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        ser.close()


if __name__ == "__main__":
    read_sensor_data()
