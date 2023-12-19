from calendar import c
import imghdr
import json
import os
from re import S

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QScrollArea, QWidget
from PyQt5.uic import loadUi

from .path import resolveUi, resolveData, resolveImage
from printer import Printer
from config import Config

class QPreview(QDialog):
    printer = None
    
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('preview.ui'), self)
        
        self.ipAddress = self.findChildren(QLabel, 'ipAddress')[0];
        self.scrollArea = self.findChildren(QScrollArea, 'scrollArea')[0];
        self.label = self.findChildren(QLabel, 'label')[0];
        self.refresh = self.findChildren(QPushButton, 'refresh')[0];

        self.refresh.clicked.connect(self.onRefresh)
        self.scrollArea.wheelEvent = lambda event: self.zoom(event)
        
        self.lastMousePos = QPoint()
        
    def onConnect(self, ipaddr):
        self.printer = Printer(ipaddr)
        self.ipAddress.setText(f'{self.printer.name} ({ipaddr})');
        
        if self.printer.GetStatusInformation() != []:
            with Config() as config:
                config.data['address'] = ipaddr
                
        self.onRefresh()
        self.zoom(None)
                
    def onRefresh(self):
        # TODO: animate
        self.img = QPixmap.fromImage(QImage.fromData(self.printer.PrintPreviewCurrentCompressed()))
        self.zoom(None)
        
    def zoom(self, event):
        if not hasattr(self, 'currentZoom'):
            self.currentZoom = 1.0
           
        delta = .05 if event else 0
        
        if event:
            if event.angleDelta().y() < 0:
                delta *= -1
            
        self.currentZoom = max(min(self.currentZoom + delta, 2.0), 0.25)
        rescaled = self.img.scaled(self.img.width() * self.currentZoom, self.img.height() * self.currentZoom)
        self.label.setPixmap(rescaled)
        self.label.resize(rescaled.size())
        
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.lastMousePos = event.pos()
       
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.lastMousePos
            self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().value() - delta.y())
            self.scrollArea.horizontalScrollBar().setValue(self.scrollArea.horizontalScrollBar().value() - delta.x())
            self.lastMousePos = event.pos()

