import serial
import struct
import time

def read_sensor_data():
    ser = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=460800,
        timeout=0.05
    )
    try:
        while True:
            start_time = time.time()
            # Read a packet of 216 bytes
            data = ser.read(216)
            if len(data) == 216:
                # Unpack the data according to the specified format
                frame_head, frame_type, frame_length, package_type, *sensor_values, checksum = struct.unpack('<HBHB208BH', data)
                # Check frame head, frame type, frame length, and package type
                if frame_head in (0x5Aa5, 0xA55A) and frame_type == 0x01 and frame_length == 0x00D6 and package_type == 0x01:
                    # Calculate the checksum (sum of all bytes except the last 2)
                    calculated_checksum = sum(data[:-2]) & 0xFFFF
                    # Validate the checksum
                    if calculated_checksum == checksum:
                        print("Data received correctly. Sensor values:")
                        for i, value in enumerate(sensor_values, 1):
                            print(f"{i:3d}: {value:3d}", end="  ")
                            if i % 16 == 0:  # New line every 16 values for readability
                                print()
                        print()  # Extra newline at the end
                    else:
                        print(f"Checksum error. Calculated: {calculated_checksum:04X}, Received: {checksum:04X}")
                else:
                    print(f"Invalid packet structure. Head: {frame_head:04X}, Type: {frame_type:02X}, Length: {frame_length:04X}, Package: {package_type:02X}")
            else:
                print(f"Incomplete data packet received. Expected 216 bytes, got {len(data)} bytes.")
            
            elapsed = time.time() - start_time
            if elapsed < 0.05:
                time.sleep(0.05 - elapsed)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        ser.close()

if __name__ == "__main__":
    read_sensor_data()
