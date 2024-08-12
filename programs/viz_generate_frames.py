#!/usr/bin/env python3
"""
This script is designed to visualize force and pressure data from two HDF5 files using sensor maps.
It processes and visualizes both static and dynamic data, including synchronized video playback
to match the force data timeline, providing a comprehensive overview of sensor behavior over time.

Command Line Arguments:
    hdf5_path1 : Specifies the path to the first HDF5 file containing Velostat sensor pressure data.
    hdf5_path2 : Specifies the path to the second HDF5 file containing Velostat sensor pressure data.
    video_path : Path to the video file synchronized with the force data (Requires same start and end time as the data)
    e.g. python viz_generate_frames.py data/2024-07-25_normal_shoes/nrshoes_left_stone2.h5 data/2024-07-25_normal_shoes/nrshoes_left_stone2.MOV

Usage:
    Run the script with paths to two HDF5 files and a video file to start the data visualization process:
        python script_name.py hdf5_path1 hdf5_path2 video_path

Features:
    - Reads and processes force data from HDF5 files, including data about sensor positions and timestamps.
    - Displays synchronized video alongside real-time sensor data visualizations.
    - Uses a color-mapped scatter plot to represent sensor data on images of the sensor layout.
    - Dynamically updates visualizations as the video progresses to show changes in force over time.
    - Allows examination of average pressure over time in a shared x-axis plot for comparison between two datasets.
    - Saves each frame of the visualization to an output directory for further use or examination.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import h5py
import cv2
import os
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import LogLocator, ScalarFormatter
import argparse
from velostat_sensor_to_pressure import lookup_pressure
from scipy.signal import find_peaks, butter, filtfilt


# Parse command line arguments for the HDF5 files
parser = argparse.ArgumentParser(description='Visualize force data from two HDF5 files with sensor maps.')
parser.add_argument('hdf5_path1', help='Path to the first HDF5 file containing force data.')
parser.add_argument('video_path', help='Path to the video file synchronized with the force data.')
args = parser.parse_args()


def load_data(hdf5_path):
    with h5py.File(hdf5_path, 'r') as file:
        dataset_name = list(file.keys())[0]
        # if dataset_name == 'e-skin':
        #     points_df = pd.read_csv('config/e-skin_foot_force_cell_positions.csv')
        #     image_path = 'images/e-skin_foot_sensor.png'
        #     image_height_mm = 314
        #     scatter_size = 350
        #     label = 'E-Skin Shoe Right'
        # elif dataset_name == 'sensor_data':
        #     points_df = pd.read_csv('config/foil_sensor_positions_right.csv')
        #     image_path = 'images/foot_sole_sensor_scan_right.png'
        #     image_height_mm = 255
        #     scatter_size = 150
        #     label = 'Velostat Sensor Right'
        
        # our sensor is labeled with 'Velostat Sensor **'
        if dataset_name == 'sensor_left':
            points_df = pd.read_csv('config/foil_sensor_positions_left.csv')
            image_path = 'images/foot_sole_sensor_scan_left.png'
            image_height_mm = 255
            scatter_size = 150
            label = 'Velostat Sensor Left'
            
        else:
            raise ValueError("HDF5 dataset not supported.")
        
        data = file[dataset_name][:]

        # Remember to modify this if your walking video and the collected data are not synchronized.
        # You can use "index_find.py" to find the corresponding values of index_start and index_end for each set of collected data.
        index_start= 27
        index_end = 151

        # timestamps = [datetime.fromtimestamp(ts / 1e9) for ts in data[:, 0]]
        timestamps = [datetime.fromtimestamp(ts / 1e9) for ts in data[index_start:index_end, 0]]
        
        # sensor_values = data[:, 1:]
        # sensor_values = data[60:355,1:]
        sensor_values = data[index_start:index_end,1:]
        points_df = points_df.sort_values(by='ID', na_position='first')
        
        return timestamps, sensor_values, points_df, image_path, image_height_mm, scatter_size, label
    

def create_video_from_frames(frames_directory, output_video_path, fps):
    # Get the list of frame files
    frame_files = [f for f in sorted(os.listdir(frames_directory)) if f.endswith('.png')]
    # Read the first frame to get the frame size
    frame = cv2.imread(os.path.join(frames_directory, frame_files[0]))
    height, width, layers = frame.shape
    
    # Initialize the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for mp4
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    # Write each frame to the video
    for frame_file in frame_files:
        frame = cv2.imread(os.path.join(frames_directory, frame_file))
        video_writer.write(frame)
    
    # Release the video writer
    video_writer.release()
    print(f"Video saved to {output_video_path}")


timestamps1, sensor_values1, points_df1, image_path1, image_height_mm1, scatter_size1, label1 = load_data(args.hdf5_path1)

# Convert sensor value to pressure in kPA
sensor_values1 = lookup_pressure(sensor_values1) / 1e3

# Create main figure and subplots
fig = plt.figure(figsize=(14.6, 8))
gs = GridSpec(2, 11, figure=fig)
ax0 = fig.add_subplot(gs[0, :5])
ax1 = fig.add_subplot(gs[1, :5])
ax2 = fig.add_subplot(gs[:, 5:8])

# Load the video
cap = cv2.VideoCapture(args.video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Video display in ax0
frame_number = 0
ret, frame = cap.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
im_video = ax0.imshow(frame)
ax0.axis('off')  # Hide axes

# Plotting the time series in ax1
ax1.plot(timestamps1, np.mean(sensor_values1, axis=1), label=label1)
ax1.set_title('Average Pressure Over Time')
ax1.set_xlabel('UTC Time')
ax1.set_ylabel('Average Pressure (kPa)')
locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
formatter = mdates.ConciseDateFormatter(locator)
ax1.xaxis.set_major_locator(locator)
ax1.xaxis.set_major_formatter(formatter)
# ax1.set_xlim([min(timestamps1[0], timestamps2[0]), max(timestamps1[-1], timestamps2[-1])])
ax1.grid(True)
ax1.legend()

# Set the y-axis limit
ax1.set_ylim(top=8)

# Vertical line on the time series plot
vline = ax1.axvline(timestamps1[0], color='r')

# Color normalization
norm = LogNorm(vmin=sensor_values1.min()*3.0, vmax=65) # vmax=sensor_values1.max()*0.7, 

# Setting up scatter plots
scatters1 = []
scatters2 = []
sensor_mask1 = np.zeros(sensor_values1.shape[1], dtype=bool) 
for ax, image_path, image_height_mm, scatter_size, points_df, sensor_values, sensor_mask, label in zip(
    [ax2],
    [image_path1],
    [image_height_mm1],
    [scatter_size1],
    [points_df1],
    [sensor_values1],
    [sensor_mask1],
    [label1]):
    
    image = plt.imread(image_path)
    image_width_mm = (image.shape[1] / image.shape[0]) * image_height_mm
    ax.imshow(image, extent=[0, image_width_mm, 0, image_height_mm], cmap='gray', alpha=0.2)
    ax.set_title(label)
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Height (mm)')

    # Scatter plot for sensor data
    scatters = []
    for index, row in points_df.iterrows():
        sensor_id = int(row['ID']) - 1
        sensor_mask[sensor_id] = True
        sensor_value = sensor_values[0, sensor_id]
        scatter = ax.scatter(row['X_in_mm'], row['Y_in_mm'], color=plt.cm.jet(norm(sensor_value)), s=scatter_size)
        scatters.append(scatter)
    if ax == ax2:
        scatters1 = scatters
    else:
        scatters2 = scatters

# Colorbar setup
sm = plt.cm.ScalarMappable(cmap='jet', norm=norm)
cbar = plt.colorbar(sm, ax=ax2, label='Pressure (kPa)')

# Define the number of ticks using LogLocator
locator = LogLocator(subs='all')
cbar.ax.yaxis.set_major_locator(locator)

# Formatter for the Colorbar ticks
formatter = ScalarFormatter()
formatter.set_scientific(False)
cbar.ax.yaxis.set_major_formatter(formatter)

# Create a directory to store frames
output_dir = 'frames/nrshoes_stone2'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

plt.tight_layout()

for frame_number , time in enumerate(np.linspace(timestamps1[0], timestamps1[-1], total_frames)):
    # Extract index nearest to selected time
    idx1 = (np.abs(np.array(mdates.date2num(timestamps1)) - mdates.date2num(time))).argmin()
    
    # Update the video frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im_video.set_data(frame)
    
    # Update Scatter
    new_data1 = sensor_values1[idx1, sensor_mask1]
    for scatter, new_value in zip(scatters1, new_data1):
        scatter.set_facecolor(plt.cm.jet(norm(new_value)))
        scatter.set_edgecolor(plt.cm.jet(norm(new_value)))
    fig.canvas.draw_idle()
    
    # Update the marker line
    vline.set_xdata([timestamps1[idx1], timestamps1[idx1]])
    
    plt.savefig(os.path.join(output_dir, f'frame_{frame_number:04d}.png'), dpi=200)


# # Define the frames directory and output video path, if you want to use def create_video_from_frames()
# frames_directory = '../viz_frames'
# output_video_path = '../output_video.mp4'
# fps = 30  # Set the frame rate as needed

# # Create the video from frames
# create_video_from_frames(frames_directory, output_video_path, fps)
