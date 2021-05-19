# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang

"""
This module declares all constants that will not change during program running, such as configuration parameters
of the serial port, physical parameters of the sensor, control parameters of the sensor, machine learning model,
etc.
"""

import serial
from joblib import load
import BLE as blec

# Configuration of the serial port
serialPortName = 'COM4'
serialBaudRate = 230400
serialDataBits = serial.EIGHTBITS
serialParity = serial.PARITY_NONE
serialByteOrder = 'littleEndian'
serialStopBits = serial.STOPBITS_ONE
serialTimeout = None
ble = blec.BLE()

# ADC parameter
dacRef = 2.5  # Reference voltage of the DAC/ADC on the microcontroller
dacRefOffset = dacRef / 2  # The measurement voltage is shifted up by this voltage to be able to measure negative voltage differences down to (-1) * dacRefOffset.
dacNMax = 4095  # Maximum value of a digital conversion

# Sensor array parameter
sensor_num_x = 6  # Size of the sensor matrix in x direction
sensor_num_y = 6  # Size of the sensor matrix in y direction
xMin = 0  # Minimum x index of the sensors that shall be measured
xMax = 5  # Maximum x index
yMin = 0  # Minimum y index
yMax = 5  # Maximum y index

# Get sensor parameter
delayMeas = 100
delaySwitch = 500
mValues = 4

durationMeas = 600

# Machine learning model
svr_model = load('.\\models\\svr.joblib')
krr_model = load('.\\models\\krr.joblib')
knn_model = load('.\\models\\knn.joblib')
