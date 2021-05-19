# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang

"""
In this module, all command constants and command functions are declared. The command constants store the byte
commands that the sensor controller can recognize. The command functions are used to send the corresponding byte
commands to the sensor controller. In addition, this module also contains the function read_measurement which is used to
calculate the sensor surface coordinates using a machine learning model.
"""

import global_variable as glv
import global_constant as glc
import numpy as np
import time
import BLE



"""
The global constant stores all control commands of the sensor controller. See instruction 'smartNIV- Communication 
Protokoll' for more detail 
"""
UART_TX_TEST = bytes([1])
LED_SET = bytes([2])
GET_SENSOR_ONCE = bytes([3])
GET_SENSOR_CONT = bytes([4])
SET_OFFSET_MEASURE = bytes([5])
SET_OFFSET_MANUAL = bytes([6])
SET_GAIN = bytes([7])
GAIN_LIST = {'2': bytes([7]), '50': bytes([0]),
             '100': bytes([1]), '200': bytes([2]),
             '400': bytes([3]), '600': bytes([4]),
             '800': bytes([5]), '1000': bytes([6])}
MEASUREMENT_STOP = bytes([8])
GET_SFREQ = bytes([9])


def start_measurement(mode):
    """ Command  sensor controller to start getting the sensor signal once or continuously.

    The function writes GET_SENSOR_ONCE or GET_SENSOR_CONT command to the serial port according to argument 'mode'. As
    a result, the sensor controller will start getting the sensor signal once or continuously.

    Args:
        mode (str): The mode of getting sensor signal. Optional value: 's' or 'c'. 's' means single. The function
                    sends GET_SENSOR_ONCE. 'c' means continuously. The function sends GET_SENSOR_CONT.

    Returns:
        None

    """
    if mode == 's':
        # glv.serial_port.write(GET_SENSOR_ONCE)
        pass
    elif mode == 'c':

        # glv.serial_port.write(GET_SENSOR_CONT)
        glv.measurement_running = True
    else:
        return

    # glv.serial_port.write(bytes([glc.xMin]))
    # glv.serial_port.write(bytes([glc.xMax]))
    # glv.serial_port.write(bytes([glc.yMin]))
    # glv.serial_port.write(bytes([glc.yMax]))
    # glv.serial_port.write(bytes([glc.mValues]))

    # delaySwitchLow = bytes([glc.delaySwitch & 255])
    # delaySwitchHigh = bytes([glc.delaySwitch >> 8])
    # glv.serial_port.write(delaySwitchLow)
    # glv.serial_port.write(delaySwitchHigh)
    #
    # delayMeasLow = bytes([glc.delayMeas & 255])
    # delayMeasHigh = bytes([glc.delayMeas >> 8])
    # glv.serial_port.write(delayMeasLow)
    # glv.serial_port.write(delayMeasHigh)


def set_offset():
    """Command sensor controller to set offset automatically

    The function write SET_OFFSET_MEASURE to the serial port. As a result, the sensor controller sets offset
    automatically, which means that the current voltage is set to zero.

    Returns:
        None

    """
    glv.serial_port.write(SET_OFFSET_MEASURE)

    temp_bytes = glv.serial_port.read(72)
    temp_float = np.frombuffer(temp_bytes, dtype=np.uint16).reshape(glc.sensor_num_y, glc.sensor_num_x).astype(np.float)
    glv.offset = ((temp_float / float(glc.dacNMax)) * glc.dacRef) - glc.dacRefOffset
    glv.sensor_enable[glv.offset > 1.2] = 0
    glv.sensor_enable[glv.offset < -1] = 0


def set_gain(gain):
    """Command sensor controller to set gain.

    The function writes SET_GAIN + gain value to the serial port. As a result, the sensor controller sets the
    amplification factor from the bridge to the ADC.

    Args:
        gain (int): the amplification factor from the bridge to the ADC

    Returns:
        None

    """
    glv.serial_port.write(SET_GAIN)
    glv.serial_port.write(GAIN_LIST[gain])


def serial_test():
    """Test whether the computer and the sensor controller have successfully established a serial transmission.

    The function writes UART_TX_TEST to the serial port. As a result, If transmission is successful, the sensor
    controller returns bytes "Test\0". If not, returns nothing.

    Returns:
        response (bytes): The return value of the  sensor controller.

    """
    glv.serial_port.write(UART_TX_TEST)
    response = glv.serial_port.read(5)

    return response


def led_on():
    """Command the sensor controller to turn on the LED light on the controller PCB.

    The function writes LED_SET + 0x01 to the serial port. As a result, the sensor controller  turn on the LED light
    on the controller PCB.

    Returns:
        None

    """
    glv.serial_port.write(LED_SET)
    glv.serial_port.write(bytes([1]))
    print('led on')


def led_off():
    """Command the sensor controller to turn off the LED light on the controller PCB.

    The function writes LED_SET + 0x00 to the serial port. As a result, the sensor controller turn off the LED light
    on the controller PCB.

    Returns:
        None

    """
    glv.serial_port.write(LED_SET)
    glv.serial_port.write(bytes([0]))
    print('led off')


def stop_measurement():
    """Command the sensor controller to stop getting sensor signal.

    The function writes MEASUREMENT_STOP to the serial port. As a result, the sensor controller stop getting sensor
    signal.
    In addition, the function  set flag measurement_running False, so that the program jumpy out of the loop
    to read data from serial port.
    The function also clear the serial port buffer to ensure no residual data for later reading.

    Returns:
        None

    """
    glv.measurement_running = False
    # glv.serial_port.write(MEASUREMENT_STOP)
    # time.sleep(0.2)
    # glv.serial_port.reset_input_buffer()
    pass


def read_measurement():
    """Read serial port and surface reconstruction using machine learning model in a dead loop.

    The function calls a dead loop. In the dead loop, the sensor voltage in the serial port sent by microcontroller
    is read continuously.
    Then based on the read voltage surface vertices coordinates are computed using machine
    learning model.
    Finally, The voltage data and coordinates data are stores in global variable sensor_data_sharing
    for visualization in graph.py.
    Once the microcontroller stops get sensor data, the loop is over.

    Returns:
        None

    """
    while True:
        # temp_bytes = glv.serial_port.read(72)
        #
        # # voltage
        # temp_float = np.frombuffer(temp_bytes, dtype=np.uint16).reshape(glc.sensor_num_y, glc.sensor_num_x).astype(np.float)
        # start = time.time()
        temp_data = glc.ble.BLE_data_update()
        print(temp_data)
        glv.sensor_v = BLE.dataDecoder(temp_data)
        # print(time.time() - start)

        # glv.sensor_v = ((temp_data / float(glc.dacNMax)) * glc.dacRef) - glc.dacRefOffset
        # glv.sensor_v = glv.sensor_v * glv.sensor_enable

        # x-,y-,z-coordinates
        # Because the input variables of the defect sensors V12, V25 and V30 are deleted when the model is trained.
        # So the corresponding input variables of the new observation here also have to be deleted
        sensor_values_delete_zero = np.delete(glv.sensor_v, [12, 25, 30]).reshape(1,-1)

        displacement_svr = glc.svr_model.predict(sensor_values_delete_zero)
        displacement_krr = glc.svr_model.predict(sensor_values_delete_zero)
        displacement_knn = glc.svr_model.predict(sensor_values_delete_zero)
        displacement = (displacement_svr + displacement_krr + displacement_knn) / 3

        x = displacement[:, :36].reshape(6, 6)
        y = displacement[:, 36:72].reshape(6, 6)
        z = displacement[:, 72:].reshape(6, 6)
        glv.sensor_xyz = [x, y, z]

        glv.sensor_data_sharing[:] = [glv.sensor_v, glv.sensor_xyz]

        if not glv.measurement_running:
            return
