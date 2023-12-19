import json
import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.uic import loadUi

from .path import resolveUi, resolveData
from printer import Printer
from config import Config

class QPreview(QDialog):
    printer = None
    
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('preview.ui'), self)
        
        self.ipAddress = self.findChildren(QLabel, 'ipAddress')[0];
        
    def onConnect(self, ipaddr):
        self.printer = Printer(ipaddr)
        self.ipAddress.setText(ipaddr);
        
        if self.printer.GetStatusInformation() != []:
            with Config() as config:
                config.data['address'] = ipaddr
                   