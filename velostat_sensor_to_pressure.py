"""
This module provides functionality to convert sensor output values from the Velostat sensor to pressure in Pa using linear 
interpolation. The data used for interpolation is based on experimental measurements relating sensor outputs to pressures.

Usage:
    This module contains a function `lookup_pressure` which takes a sensor output value and returns the estimated pressure 
    in Pa. It can be imported and used in other scripts as needed.

Example:
    from velostat_sensor_to_pressure import lookup_pressure
    pressure = lookup_pressure(150)
    print(f"Estimated Pressure: {pressure:.2f} Pa")
"""

import numpy as np
from scipy.interpolate import interp1d

# Initialize data arrays for sensor output and corresponding pressures in Pascal
sensor_output = np.array([
    0.461538, 3.5, 16.269231, 32.730769, 56.153846, 84.307692,
    105.884615, 111.153846, 126.346154, 130.038462, 140.615385,
    143.615385, 151.230769, 153.461538, 160.846154, 163.076923,
    169.153846, 171.115385, 176.923077, 178.807692, 183.423077,
    185.400000, 189.450000, 189.875000, 194.000000, 250.000000
])

pressure_pa = np.array([
    1620.737016, 3781.719703, 5942.702391, 8103.685078, 10264.667766,
    12425.650453, 14586.633141, 15126.878813, 16747.615828, 17287.861500,
    18908.598516, 19448.844188, 21069.581203, 21609.826875, 23230.563891,
    23770.809563, 25391.546578, 25931.792250, 27552.529266, 28092.774938,
    29713.511953, 30253.757625, 31874.494641, 32414.740313, 34575.723000,
    94542.992579
])

# Set up the interpolation function with extrapolation
_pressure_from_sensor_output = interp1d(sensor_output, pressure_pa, fill_value="extrapolate")

def lookup_pressure(sensor_value):
    """
    Convert a sensor output value to pressure in Pa using linear interpolation.

    Args:
        sensor_value (float): The sensor output value to convert.

    Returns:
        float: The estimated pressure in Pa.
    """
    return _pressure_from_sensor_output(sensor_value)
