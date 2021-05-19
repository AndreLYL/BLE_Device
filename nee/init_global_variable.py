# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang
"""
This module is used to initialize the global variables global constants in global_variable.py.
"""

import global_constant as glc
import global_variable as glv
import numpy as np
import multiprocessing


def init_global_variable():
    """Initialize the variables in global_variable.py


    Returns:
        None

    """
    glv.measurement_running = False

    glv.offset = np.zeros((glc.sensor_num_y, glc.sensor_num_x))
    glv.sensor_enable = np.ones((glc.sensor_num_y, glc.sensor_num_x))

    glv.sensor_v = np.zeros((glc.sensor_num_x, glc.sensor_num_y))

    x, y = np.meshgrid(np.linspace(-12.5, 12.5, 6), np.linspace(-12.5, 12.5, 6))
    z = np.zeros((glc.sensor_num_y, glc.sensor_num_x))
    glv.sensor_xyz = [x, y, z]

    glv.sensor_data_sharing = multiprocessing.Manager().list([glv.sensor_v, glv.sensor_xyz])
