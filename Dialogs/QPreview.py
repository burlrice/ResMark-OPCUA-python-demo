from calendar import c
import imghdr
import json
import os
from re import S
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QMovie, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QScrollArea, QWidget
from PyQt5.uic import loadUi

from .path import resolveUi, resolveData, resolveImage
from printer import Printer
from config import Config

class QPreview(QDialog):
    printer = None
    refreshComplete = pyqtSignal(QPixmap)
    
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('preview.ui'), self)
        
        self.ipAddress = self.findChildren(QLabel, 'ipAddress')[0];
        self.scrollArea = self.findChildren(QScrollArea, 'scrollArea')[0];
        self.label = self.findChildren(QLabel, 'label')[0];
        self.refresh = self.findChildren(QPushButton, 'refresh')[0];

        self.refreshIcon = self.refresh.icon()
        self.refreshComplete.connect(self.onRefreshComplete)
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
                
    def onRefresh(self):
        self.movie = QMovie(resolveImage('Refresh.gif'))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start();
        self.thread = threading.Thread(target=self.PrintPreviewCurrentCompressed)
        self.thread.start()        

    def PrintPreviewCurrentCompressed(self):
        self.refreshComplete.emit(QPixmap.fromImage(QImage.fromData(self.printer.PrintPreviewCurrentCompressed())))
        
    def onFrameChanged(self):
        self.refresh.setIcon(QIcon(self.movie.currentPixmap()))
    
    @pyqtSlot(QPixmap)
    def onRefreshComplete(self, img):
        self.img = img
        self.zoom(None)
        self.movie.stop()
        self.refresh.setIcon(self.refreshIcon)
        
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

