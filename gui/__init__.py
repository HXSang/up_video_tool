import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Load file untitled.ui nằm cùng thư mục với main.py
        ui_path = os.path.join(os.path.dirname(__file__), "untitled.ui")
        uic.loadUi(ui_path, self)

        QTimer.singleShot(0, self.adjust_table_columns)
