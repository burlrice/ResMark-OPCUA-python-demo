import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.uic import loadUi

from .path import resolveUi

class QSearch(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('search.ui'), self)

        self.refresh = self.findChildren(QPushButton, 'refresh')[0];
        self.refresh.clicked.connect(lambda: print('refresh'))
