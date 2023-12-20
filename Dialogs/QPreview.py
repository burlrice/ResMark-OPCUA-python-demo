import json
import os
import re
import threading
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QMovie, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QScrollArea, QToolButton, QWidget
from PyQt5.uic import loadUi

from Dialogs.QMessages import QMessages
from Dialogs.busy import Busy

from .path import resolveTopMostWidget, resolveUi, resolveData, resolveImage
from printer import Printer
from config import Config
from message import Message

class QPreview(QDialog):
    printer = None
    refreshComplete = pyqtSignal(QPixmap)
    startMessage = pyqtSignal(str)
    status = pyqtSignal(str)
    state = {}
    lastImageHashKey = 0
    
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('preview.ui'), self)
        
        self.label = self.findChildren(QLabel, 'label')[0];
        self.ipAddress = self.findChildren(QLabel, 'ipAddress')[0];
        self.message = self.findChildren(QLabel, 'message')[0];
        self.count = self.findChildren(QLabel, 'count')[0];
        self.lineSpeed = self.findChildren(QLabel, 'lineSpeed')[0];
        self.errors = self.findChildren(QToolButton, 'errors')[0];
        self.scrollArea = self.findChildren(QScrollArea, 'scrollArea')[0];
        self.refresh = self.findChildren(QPushButton, 'refresh')[0];

        self.start = self.findChildren(QPushButton, 'start')[0];
        self.pause = self.findChildren(QPushButton, 'pause')[0];
        self.stop = self.findChildren(QPushButton, 'stop')[0];

        self.refreshComplete.connect(self.onRefreshComplete)
        self.startMessage.connect(self.onStartMessage)
        self.status.connect(self.onStatus)
        self.refreshIcon = self.refresh.icon()
        self.scrollArea.wheelEvent = lambda event: self.zoom(event)

        self.refresh.clicked.connect(self.onRefresh)
        self.start.clicked.connect(self.onStart)
        self.pause.clicked.connect(self.onPause)
        self.stop.clicked.connect(self.onStop)
        
        self.lastMousePos = QPoint()
        
        self.running = threading.Event()
        threading.Thread(target=self.statusThread, args=(self.running, )).start()
       
    def onConnect(self, ipaddr):
        self.printer = Printer(ipaddr)
        self.ipAddress.setText(f'{self.printer.name} ({ipaddr})');
        
        if self.printer.GetStatusInformation() != []:
            with Config() as config:
                config.data['address'] = ipaddr
                
    def onRefresh(self):
        self.movie = QMovie(resolveImage('Refresh.gif'))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start();
        threading.Thread(target=self.PrintPreviewCurrentCompressed).start()

    def PrintPreviewCurrentCompressed(self):
        img = self.printer.PrintPreviewCurrentCompressed()
        if img:
            self.refreshComplete.emit(QPixmap.fromImage(QImage.fromData(img)))
        else:
            self.refreshComplete.emit(QPixmap())    
            
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
            
        if self.img:
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
            
    def statusThread(self, running):
        while not running.is_set():
            time.sleep(1)
            self.status.emit(json.dumps(self.printer.GetStatusInformation()))
            
    def onStart(self):
        main = resolveTopMostWidget(self);
        messages = QMessages(self.startMessage)
        messages.messages = self.printer.GetStoredMessageList()
        main.onPushNavigationStack(messages)

    @pyqtSlot(str)
    def onStartMessage(self, message):
        with Busy(self) as busy:
            doc = Message(self.printer.RecallMessage(message))
            
            if len(doc.counts):
                print('counts')

            if len(doc.variables):
                print('variables')
                
            self.printer.PathPrintStoredMessage('', message)
            self.img = None

            while self.img == None:
                self.img = self.printer.PrintPreviewCurrentCompressed()
                time.sleep(.25)
        
            self.currentZoom = 1.0
    
    def onPause(self):
        if self.state.get('State') == 'Paused':
            self.printer.ResumePrinting()
        else:
            self.printer.StopPrinting()
            
    def onStop(self):
        self.printer.CancelPrinting()
            
    @pyqtSlot(str)
    def onStatus(self, jsonData):
        data = json.loads(jsonData)

        if len(data) >= 7:
            self.state = {
                'State': data[0],
                'Message': data[1],
                'Line speed': data[2],
                'Count': format(str(data[3][0]).split(':')[1]),
                'Consumable': data[4],
                'Errors': data[5],
                'Warnings': data[6],
                'ImageHashKey': data[7]
            }
            
            self.message.setText(self.state['Message'])
            
            if self.lastImageHashKey != self.state['ImageHashKey']:
                self.lastImageHashKey = self.state['ImageHashKey']
                self.onRefresh()
        
            states = {
                'Printing': { 'images': [ 'play.png', 'pause.png', 'stop.png' ] },
                'Paused': { 'images': [ 'play.png', 'resume.png', 'stop.png' ] },
                'Idle': { 'images': [ 'play.png', '', '' ] },
                }
            images = {
                Printer.State.Ok: '',
                Printer.State.Warning: 'warning.png',
                Printer.State.Error: 'error.png',
                }
        
            #print(json.dumps(self.state, indent=4))
            
            self.start.setIcon(QIcon(QPixmap(resolveImage(states[self.state['State']]['images'][0]))))
            self.pause.setIcon(QIcon(QPixmap(resolveImage(states[self.state['State']]['images'][1]))))
            self.stop.setIcon(QIcon(QPixmap(resolveImage(states[self.state['State']]['images'][2]))))
            self.count.setText(f'''Product count: {self.state['Count']}''')
            self.lineSpeed.setText('{:.2f} f/min'.format(self.state['Line speed']))
            
            self.errors.setText("\n" + "\n\n".join(['\n'.join([f"{key}: {item}" for item in value]) for key, value in self.printer.errors.items()]))
            self.errors.setIcon(QIcon(QPixmap(resolveImage(images[self.printer.GetState()]))))