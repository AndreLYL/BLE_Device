# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang

"""
This module declares all global variables whose value will change during program runtime, such as serial port
objects, dead-loop interrupt flags, sensor voltage data, surface coordinate data, multi-process shared data, etc.
"""

serial_port = None  # serial port objects

measurement_running = False  # interrupt flags of reading sensor measurements

plot_running = False  # interrupt flags of plotting 3D bar plot and 3D surface plot

offset = None
sensor_enable = None  # Working sensor after diagnose

sensor_v = None  # Array of sensor voltages
sensor_xyz = None  # Array of sensor surface vertices coordinates

sensor_data_sharing = None  # Multiprocessing sharing variable for visualization of voltages and surface
