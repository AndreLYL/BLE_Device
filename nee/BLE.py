# @Time    : 2021/5/18
# @Author  : Yinglong Li

import pygatt
import time
from binascii import hexlify
# import graphBLE as gh
import numpy as np
import logging


class BLE:
    def __init__(self):
        # BLED112 Address information
        self.BLE_COM_PORT = 'COM4'
        self.BLE_MAC = '00:A0:50:AA:BB:FF'
        self.BLE_UUID = "f81e56d4-54d5-4dd4-be72-8291a336f21e"

        # enable the debug mode
        self.logging_enable = False

        # initialize the adapter and ble device
        self.adapter = None
        self.device = None

    def BLE_connection_setup(self):
        self.adapter = pygatt.BGAPIBackend(serial_port=self.BLE_COM_PORT)

        # Enable logging to get debug information
        if self.logging_enable:
            logging.basicConfig()
            logging.getLogger('pygatt').setLevel(logging.DEBUG)

        self.adapter.start()
        device_list = self.adapter.scan(timeout=5)
        print("Device List:")
        print(device_list)
        self.device = self.adapter.connect(self.BLE_MAC, timeout=20)

    def BLE_data_update(self):
        data = []

        def handle_data(handle, value):
            """
            handle -- integer, characteristic read handle the data was received on
            value -- bytearray, the data returned in the notification
            """
            # print("Received data: %s" % hexlify(value))
            data.append(hexlify(value))

        if self.device is None:
            print("Error, BLE device not initialized.")
        else:
            self.device.subscribe(self.BLE_UUID, callback=handle_data)
            time.sleep(0.2)
            self.device.unsubscribe(self.BLE_UUID)
        return data


def dataDecoder(data):
    """Decode the data package from the BLED1112 to float array(6*6)
    Args:
    Returns: sensor_data: 6*6 float array
    """
    real_data = []
    for package in data:
        for i in range(4, len(package), 3):
            real_data.append(
                float(int(chr(package[i])) * 0.01 + int(chr(package[i + 1])) * 0.1 + int(chr(package[i + 2])) * 1.0))
    # print(real_data)
    sensor_data = np.array(real_data)
    # print(len(sensor_data))
    return sensor_data.reshape((6, 6))


if __name__ == "__main__":

    ble = BLE()
    ble.BLE_connection_setup()

    while True:
        start = time.time()
        ble_data = ble.BLE_data_update()
        # plot_data = ble_data.copy()
        # print(data)
        plot_data = dataDecoder(ble_data)
        gh.realtime_plot_v(plot_data)
        # gh.realtime_plot_xyz(sensor_data_sharing)

        print(time.time() - start)
