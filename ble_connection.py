import pygatt
import time
from binascii import hexlify
import matplotlib.pyplot as plt
import graph as gh
import numpy as np

BLE_MAC = '00:A0:50:AA:BB:FF'
BLE_UUID = "f81e56d4-54d5-4dd4-be72-8291a336f21e"

data = []

def dataDecoder():
    """Decode the data package from the BLED1112 to float array(6*6)

    Args:

    Returns:
        sensor_data: 6*6 float array

    """
    real_data = []
    for package in data:
        for i in range(4, len(package), 3):
            real_data.append(float(int(chr(package[i])) * 0.01 + int(chr(package[i + 1])) * 0.1 + int(chr(package[i + 2])) * 1.0))
    # print(real_data)
    sensor_data = np.array(real_data)
    return sensor_data.reshape((6, 6))

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    # print("Received data: %s" % hexlify(value))
    data.append(hexlify(value))


if __name__ == "__main__":

    adapter = pygatt.BGAPIBackend(serial_port='COM9')

    try:
        adapter.start()
        device_list = adapter.scan(timeout=5)
        print("Device List:")
        print(device_list)

        try:
            device = adapter.connect(BLE_MAC, timeout=20)

        except:
            print("Couldn't connecting to device, retrying...")
            device = adapter.connect(BLE_MAC, timeout=20)

        while True:
            start = time.time()
            device.subscribe(BLE_UUID, callback=handle_data, wait_for_response=True)

            time.sleep(0.5)
            device.unsubscribe(BLE_UUID, wait_for_response=True)

            # print(data)
            sensor_data = dataDecoder()
            gh.realtime_plot_v(sensor_data)
            data.clear()
            print(time.time() - start)
            # print(test_data)

    finally:
        adapter.stop()
        print("Adapter Stopped")


