from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtWidgets import QDialog, QListWidget, QPushButton
from PyQt5.uic import loadUi

from .path import resolveTopMostWidget, resolveUi

class QMessages(QDialog):
    messages = []
    
    def __init__(self, startMessageSignal: pyqtSignal):
        super().__init__()
        loadUi(resolveUi('messages.ui'), self)
                
        self.startMessageSignal = startMessageSignal;
        self.listWidget = self.findChildren(QListWidget, 'listWidget')[0]
        
        self.findChildren(QPushButton, 'start')[0].clicked.connect(self.onStart)
        self.findChildren(QPushButton, 'cancel')[0].clicked.connect(self.onCancel)
        self.listWidget.itemDoubleClicked.connect(lambda: self.onStart())
        
    def setVisible(self, visible: bool):
        super().setVisible(visible)
        self.listWidget.addItems(self.messages)
        
    def onStart(self):
        if self.listWidget.currentItem():
            resolveTopMostWidget(self).onPopNavigationStack()
            self.startMessageSignal.emit(self.listWidget.currentItem().text())
    
    def onCancel(self):
        resolveTopMostWidget(self).onPopNavigationStack()
        