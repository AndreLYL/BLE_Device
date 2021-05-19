# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang
"""
In this module the class of the main interface  is declared. The callback functions for  ui elements are defined
in the class. In addition, multi-threaded classes for refreshing the main interface are also declared.
"""
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import init_global_variable
import global_variable as glv
import global_constant as glc
import serial
import command as cmd
import graph
import numpy as np
import threading
import multiprocessing
# import nee.BLEconnect as blec


class MainUI(QWidget):
    """The main menu of the program

    The main menu of the program. The layout of the UI is loaded from file main.ui created by QT Designer. The ui
    elements are the attributes of the class.
    """

    def __init__(self):
        """Constructor of the class

        constructor of the class. In this function the initial status and callback function of the ui elements are
        defined. In addition the multiprocess nad multithreading are created.


        """
        super().__init__()

        # Load the UI layout which is created with PyQt.
        uic.loadUi("ui/main.ui", self)

        # Set table
        self.table_offset.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_v.setEditTriggers(QTableWidget.NoEditTriggers)
        for i in np.arange(6):
            self.table_v.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.table_v.verticalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.table_offset.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.table_offset.verticalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # Set button callback function
        self.button_connect.clicked.connect(self.connect)
        self.button_set_offset.clicked.connect(self.set_offset)
        self.button_show_graph.clicked.connect(self.show_graph)
        self.button_run_c.clicked.connect(self.run_c)
        self.button_run_s.clicked.connect(self.run_s)
        # Set buttons' enable-state
        self.button_set_offset.setEnabled(False)
        self.button_show_graph.setEnabled(False)
        self.button_run_c.setEnabled(False)
        self.button_run_s.setEnabled(False)

        # Set combobox callback function
        self.combobox_gain.currentIndexChanged.connect(self.set_gain)
        # Set comboboxes' enable-state
        self.combobox_gain.setEnabled(False)
        self.label_gain.setEnabled(False)

        # Creat a children thread in the main precess to update the UI.
        self.update_ui_thread = UpdateUI()
        self.update_ui_thread.update_table.connect(self.update_table)
        self.update_ui_thread.update_button.connect(self.update_button)

        # Creat a children thread in the main precess to read the measurement.
        self.read_measurement_thread = threading.Thread(target=cmd.read_measurement, daemon=True)

        # Creat two new process for graph.
        self.graph_process_v = multiprocessing.Process(target=graph.realtime_plot_v, args=(glv.sensor_data_sharing,))
        self.graph_process_xyz = multiprocessing.Process(target=graph.realtime_plot_xyz,
                                                         args=(glv.sensor_data_sharing,))

        # Initialization
        init_global_variable.init_global_variable()

    def connect(self):
        """The callback function of button 'Connect'.

        After clicking the button 'Connect', the serial port object is created to establish the transmission between
        the sensor controller and PC.
        The button can't be clicked twice. The second click will raise a exception and
        cause a warning window.
        In addition after clicking, the enable status of other ui elements are unlocked.

        Returns:
            None

        """
        try:
            # glv.serial_port = serial.Serial(port=glc.serialPortName,
            #                                 baudrate=glc.serialBaudRate,
            #                                 bytesize=glc.serialDataBits,
            #                                 parity=glc.serialParity,
            #                                 stopbits=glc.serialStopBits,
            #                                 timeout=glc.serialTimeout)
            # cmd.set_gain('100')
            glc.ble.BLE_connection_setup()

        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e), QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.update_ui_thread.start()
            self.button_set_offset.setEnabled(True)
            self.button_show_graph.setEnabled(True)
            self.button_run_c.setEnabled(True)
            self.button_run_s.setEnabled(True)
            self.combobox_gain.setEnabled(True)
            self.label_gain.setEnabled(True)
            QMessageBox.information(self, 'Information', 'Connection successful!', QMessageBox.Ok, QMessageBox.Ok)

    def set_offset(self):
        """The callback function of button 'Set offset'

        Returns:
            None

        """
        cmd.stop_measurement()
        self.button_run_c.setText('Run')
        cmd.set_offset()

    def set_gain(self):
        """The callback function of combobox 'gain'

        Returns:
            None

        """
        cmd.set_gain(self.combobox_gain.currentText())

    def show_graph(self):
        """The callback function of button 'Show graph'

        Returns:
            None

        """
        self.graph_process_v = multiprocessing.Process(target=graph.realtime_plot_v, args=(glv.sensor_data_sharing,))
        self.graph_process_xyz = multiprocessing.Process(target=graph.realtime_plot_xyz,
                                                         args=(glv.sensor_data_sharing,))
        self.graph_process_v.start()
        self.graph_process_xyz.start()

    def run_s(self):
        """The callback function of button 'Run 1x'

        Returns:
            None

        """
        # cmd.stop_measurement()
        # cmd.start_measurement(mode='s')
        self.read_measurement_thread = threading.Thread(target=cmd.read_measurement, daemon=True)
        self.read_measurement_thread.start()
        self.button_run_c.setText('Run')

    def run_c(self):
        """The callback function of button 'Run'

        Returns:
            None

        """
        if self.button_run_c.text() == 'Run':
            cmd.stop_measurement()
            cmd.start_measurement(mode='c')
            self.read_measurement_thread = threading.Thread(target=cmd.read_measurement, daemon=True)
            self.read_measurement_thread.start()
            self.button_run_c.setText('Stop')
        else:
            cmd.stop_measurement()
            self.button_run_c.setText('Run')

    def closeEvent(self, event):
        """ Override the method of parent class QWidget.

        The closeEvent method define the behaviour of clicking exit button 'x' of the window. Before exit the
        programm, a messagebox is called to confirm with the user if they want to exit the program. If yes,
        all measurement process and children process will be terminated to ensure that there is no possible exception
        caused by the exit of the program.


        Args:
            event: Fixed argument for method closeEvent of parent class.

        Returns:
            None

        """

        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to exit the program?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            # Stop all sub-threads and sub-processes, than wait for them to exit before exiting the main program
            # (to prevent exception raising)
            if self.read_measurement_thread.is_alive():
                cmd.stop_measurement()
                self.read_measurement_thread.join()
            if self.graph_process_v.is_alive() or self.graph_process_xyz.is_alive():
                self.graph_process_v.terminate()
                self.graph_process_xyz.terminate()
                self.graph_process_v.join()
                self.graph_process_xyz.join()
        else:
            event.ignore()

    def update_table(self):
        """Update the table of the main menu.

        Returns:
            None

        """
        sensor_v = np.around(glv.sensor_v, decimals=4)
        offset = np.around(glv.offset, decimals=4)
        for i in np.arange(6):
            for j in np.arange(6):
                self.table_v.setItem(i, j, QTableWidgetItem(str(sensor_v[i, j])))
                self.table_offset.setItem(i, j, QTableWidgetItem(str(offset[i, j])))

    def update_button(self):
        """Update the enable status of main menu's buttons

        Returns:
            None

        """
        if self.graph_process_v.is_alive() or self.graph_process_xyz.is_alive():
            self.button_show_graph.setEnabled(False)
        else:
            self.button_show_graph.setEnabled(True)


class UpdateUI(QThread):
    """Multithreading class for updating the table and buttons of the main menu.

    This is the usage of pyqt multithreading class Qthread. Visit
    https://doc.qt.io/qtforpython/PySide6/QtCore/QThread.html for details.

    """
    update_table = pyqtSignal()
    update_button = pyqtSignal()

    def run(self):
        """Define what is run in this threading

        Returns:
            None

        """
        while True:
            self.update_table.emit()  # emit signal
            self.update_button.emit()
            time.sleep(0.3)
