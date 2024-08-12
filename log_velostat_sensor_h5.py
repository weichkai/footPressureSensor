#!/usr/bin/env python3
"""
This script is designed to log sensor data from the FootSole sensors into an HDF5 file format. It can operate with sensors from either the right or left side, and connects to the appropriate serial port based on command-line input.

Command Line Arguments:
    --log_left : When this flag is specified, the script logs data from the left sensor and connects via '/dev/ttyUSB1' instead of the default right sensor on '/dev/ttyUSB0'.

Usage:
    Run the script without any arguments to start logging from the right sensor which must be connected first:
        log_velostat_sensor_h5.py

    Run the script with the --log_left flag to start logging from the left sensor which must be connected after the right sensor:
        log_velostat_sensor_h5.py --log_left
        
    Remember to modify port name to adapt your computer in line 55

Features:
    - Dynamic filename generation based on sensor side and current timestamp.
    - Continuous data acquisition and logging until interrupted by the user.
    - Automatic handling of serial connection issues and dataset creation within the HDF5 file.
    - Real-time processing and logging of sensor data based on packet integrity.
"""

import sys
import serial
import struct
import time
import h5py
import numpy as np
import datetime
import argparse

MAX_BUFFER_SIZE = 1024 * 10  # 10 KB maximum buffer size
TIMEOUT_THRESHOLD = 5  # seconds
RESYNC_ATTEMPTS = 5
PACKET_SIZE = 216

class FootSoleLogger:
    def __init__(self, use_left_sensor):
        self.use_left_sensor = use_left_sensor
        self.init_serial()
        self.generate_filename()
        self.init_hdf5()

    def generate_filename(self):
        # Get current date and time
        current_time = datetime.datetime.now()
        # Format filename based on the sensor side
        sensor_side = "sensor_left" if self.use_left_sensor else "sensor_right"
        self.hdf5_file = current_time.strftime(f"{sensor_side}_%Y-%m-%d-%H-%M-%S.h5")

    def init_serial(self):
        # Remember to modify port name to adapt your computer
        # port = '/dev/ttyUSB1' if self.use_left_sensor else '/dev/ttyUSB0'
        port = '/dev/tty.usbserial-10' if self.use_left_sensor else '/dev/ttyUSB0'
        # /dev/tty.Bluetooth-Incoming-Port 
        try:
            self.ser = serial.Serial(port, baudrate=460800, timeout=0.001)
            self.buffer = bytearray()
            print(f"Serial connection established on {port}.")
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            sys.exit(1)

    def init_hdf5(self):
        # Initialize the HDF5 file and dataset
        self.hdf5 = h5py.File(self.hdf5_file, 'a')
        dataset_name = "sensor_left" if self.use_left_sensor else "sensor_right"
        if dataset_name not in self.hdf5:
            self.hdf5.create_dataset(dataset_name, shape=(0, 209), maxshape=(None, 209), dtype='float64')

    def update_data(self):
        try:
            while self.ser.in_waiting:
                new_data = self.ser.read(self.ser.in_waiting)
                self.buffer.extend(new_data)

                while len(self.buffer) >= PACKET_SIZE:
                    if self.process_packet():
                        print("Valid packet processed.")
                    else:
                        print("Error processing packet.")

        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            self.reset_connection()

    def process_packet(self):
        packet = self.buffer[:PACKET_SIZE]
        self.buffer = self.buffer[PACKET_SIZE:]

        try:
            frame_head, frame_type, frame_length, package_type, *sensor_values, checksum = struct.unpack('<HBHB208BH', packet)
            calculated_checksum = sum(packet[:-2]) & 0xFFFF

            if calculated_checksum == checksum:
                self.log_sensor_values(sensor_values)
                return True
            else:
                print(f"Checksum error. Calculated: {calculated_checksum:04X}, Received: {checksum:04X}")

        except struct.error:
            print("Struct unpacking error")

        return False

    def log_sensor_values(self, sensor_values):
        timestamp = time.time_ns()
        data = np.array([[timestamp] + sensor_values], dtype='float64')
        dataset_name = "sensor_left" if self.use_left_sensor else "sensor_right"
        ds = self.hdf5[dataset_name]
        ds.resize(ds.shape[0] + 1, axis=0)
        ds[-1:] = data

    def reset_connection(self):
        print("Resetting serial connection...")
        self.ser.close()
        time.sleep(1)
        self.init_serial()

    def close(self):
        self.hdf5.close()
        print("HDF5 file closed.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process sensor data for FootSole Logger.")
    parser.add_argument('--log_left', action='store_true', help='Log data from the left sensor and connect via ttyUSB1')
    args = parser.parse_args()

    logger = FootSoleLogger(use_left_sensor=args.log_left)
    try:
        while True:
            logger.update_data()
    except KeyboardInterrupt:
        logger.close()
        print("Logging stopped by user.")
