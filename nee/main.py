# @Time    : 2021/3/30 22:16
# @Author  : Yang Wang

"""
This module is the entrance of the program. It creates and start the main menu of the program.

"""

import sys
from PyQt5.QtWidgets import *
from main_ui import MainUI
# import nee.BLEconnect as blec

if __name__ == '__main__':

    app = QApplication([])
    main_ui = MainUI()
    main_ui.show()
    sys.exit(app.exec_())
