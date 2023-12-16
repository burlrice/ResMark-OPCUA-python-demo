import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi

class QMainWnd(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'form.ui'), self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QMainWnd()
    widget.show()
    sys.exit(app.exec_())
