# Foot Sole Pressure Sensing With The Fullsoul

This is our repo for the Clinical Applications of Computation Medicine course, where we were able to measure the foot pressure distribution within a barefoot shoe.

<div>
  <img src="images/foot_sole_sensor_scan_right.png" width="15%" alt="Foot Sole Sensor Scan Right">
  <img src="images/sandwich.png" width="75%" alt="Sandwich Construction inside Fullsoul">
  <img src="images/result.png" width="90%" alst="results"
</div>


# Instructions to replicate our results
## Installing Dependencies
Install all the libraries that are listed in the requirements.txt with your preffered method


## Measuring Data
1. Install the snesor in the fullsoul
2. Connect the controller to both the fullsoul and your pc via usb-c cable
3. Start programm "log_velostat_sesor_h5.py"
4. Walk around and record video with a phone or camera, save in format .mp4 or .mov
5. Close program "log_velostat_sesor_h5.py"


## Visualizing Data
1. Open program "viz_generate_frames.py"
2. Change the location and names of the video and h5 data file (recorded above) in the code to match your folder structure
3. Run program "viz_generate_frames.py"



# Data
All data we recorded is available in this cloud (lrz sync&share for TUM students): https://syncandshare.lrz.de/getlink/fiNrHQxXBhm1jq8pmnKeAs/

If you have trouble accessing it, please let us know.
We could not use a google drive due to lack of space. 

# Programs
These are our programs and what each program does. For further information please look at each individual programs docstring!

1. log_velostat_sensor_h5.py: collects sensor data from the Velostat sensors.
   - Remember to modify the port name in line 55 to match your computer's configuration.
   - Ensure that the video is recorded simultaneously with the sensor data to keep them synchronized.
2. index_find.py:
   - If you forget to synchronize the walking video with the collected data, use this script to determine the correct indices for synchronization. It identifies the peak indices in your data, which you can then use to adjust the start and end points in viz_generate_frames.py.
   - Additionally, this script helps you edit the video by cutting it from the first peak to the last peak (when you are fully on your foot).
   - Update lines 80 and 81 of viz_generate_frames.py with these peak indices to ensure proper synchronization between your video and sensor data.
3. velostat_sensor_to_pressure.py: provides a function to convert Velostat sensor output values to pressure in Pascals using linear interpolation.
   - No modifications are needed for this script. The function is modular and directly used by viz_generate_frames.py.
4. viz_generate_frames.py: visualizes and analyzes sensor data alongside the video.
   - This script generates frames of the walking process, featuring three subplots: the entire walking process on the top left, the average pressure across the entire foot over time on the bottom left, and the pressure recorded at each sensor point over time on the right.
5. frames_to_video.py: creates an animation from the generated frames.
   - Always remember to update the folder paths according to your specific requirements.

# Miscelaneous
Manufacturer contact
Sensor datasheet link etc
