"""
This script aligns walking video and the collected data.

Command Line Arguments(for instance):
    python index_find.py data/2024-07-25_normal_shoes/nrshoes_left_stone2.h5    
    
Usage:
    When collecting walking video and data synchronously, if they do not start or end 
    at the same time, then the two are not synchronized. Therefore, we devised a method
    to cut the video and data, starting and ending both at peaks. 
    This script can help you find the indices of all peaks in the data. 
    Then, input the values of the first and last indices into lines 80 and 81 of viz_generate_frames.py.
    Attention: This script is only necessary if you encounter an issue with asynchronous walking video and data.
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
args = parser.parse_args()

def butter_lowpass_filter(data, cutoff, fs, order=5): 
    nyq = 0.5 * fs # Nyquist frequency
    normal_cutoff = cutoff / nyq # Get the filter coefficients
    b, a = butter(order, normal_cutoff, btype='low', analog=False) # Zero-phase filtering using filtfilt
    y = filtfilt(b, a, data) 
    
    return y 


with h5py.File(args.hdf5_path1, 'r') as file:
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
    if dataset_name == 'sensor_left':
        points_df = pd.read_csv('config/foil_sensor_positions_left.csv')
        image_path = 'images/foot_sole_sensor_scan_left.png'
        image_height_mm = 255
        scatter_size = 150
        label = 'Velostat Sensor Left'
        
    else:
        raise ValueError("HDF5 dataset not supported.")
    
    data = file[dataset_name][:]
    
    data_mean = np.mean(data[:,1:], axis=1)
    
    filtered_data = butter_lowpass_filter(data_mean, cutoff=1.5, fs=21, order=5) # 截止频率为3Hz 

    plt.plot(filtered_data)
    plt.show()
    peaks, property = find_peaks(filtered_data, height=25)
    # print(np.mean(data[:,1:], axis=1))
    print(peaks)
    # plt.plot(np.mean(data[:,1:], axis=1))
    # plt.show()
    
    
# fullsoul  
# wiese0 18,61,355
# wiese1 50,509
# stein1 70,199

# nrshoes
# wiese2 36 230
# stein1 12 192 
# stein2 27 151