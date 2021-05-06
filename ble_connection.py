import pygatt
import time
from binascii import hexlify

BLE_MAC = '00:A0:50:AA:BB:FF'
BLE_UUID = "f81e56d4-54d5-4dd4-be72-8291a336f21e"


def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: %s" % hexlify(value))
    # data.append(hexlify(value))


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

        # device.char_write_handle(0x0019, True)

        device.subscribe(BLE_UUID, callback=handle_data, wait_for_response=True)
        time.sleep(1)
        device.unsubscribe(BLE_UUID, wait_for_response=True)
        time.sleep(1)
        device.subscribe(BLE_UUID, callback=handle_data, wait_for_response=True)
        time.sleep(1)
        device.unsubscribe(BLE_UUID, wait_for_response=True)

    finally:
        adapter.stop()
        print("Adapter Stopped")
