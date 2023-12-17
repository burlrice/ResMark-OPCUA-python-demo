import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.uic import loadUi

from .path import resolveUi

class QPreview(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('preview.ui'), self)
