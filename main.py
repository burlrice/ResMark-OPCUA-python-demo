import sys
import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.uic import loadUi

from Dialogs.QSearch import QSearch
from Dialogs.QPreview import QPreview

from config import Config

class QMainWnd(QMainWindow):
    pushNavigationStack = pyqtSignal(QWidget)
    popNavigationStack = pyqtSignal()
    connect = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'form.ui'), self)
        self.navigation = []
        
        self.back = self.centralWidget().findChildren(QPushButton, 'back')[0];
        self.back.clicked.connect(lambda: self.onPopNavigationStack())
           
        self.search = self.centralWidget().findChildren(QPushButton, 'search')[0];
        self.search.clicked.connect(lambda: self.onPushNavigationStack(QSearch()))

        self.pushNavigationStack.connect(self.onPushNavigationStack)
        self.popNavigationStack.connect(self.onPopNavigationStack)
        self.connect.connect(self.onConnect)
        
        self.onPushNavigationStack(QPreview())
        config = Config()
        
        if 'address' in config.data:
            self.onConnect(config.data['address'])
            self.updateWindowText()
        else:
            self.onPushNavigationStack(QSearch())
    
    @pyqtSlot()
    def onPushNavigationStack(self, widget):
        for i in self.navigation:
            self.Client.layout().removeWidget(i)
            i.hide()
            
        self.navigation.append(widget)
        current = self.navigation[len(self.navigation) - 1]
        self.Client.layout().addWidget(current);
        self.back.setEnabled(len(self.navigation) > 1)
        self.updateWindowText()
        
    def updateWindowText(self):
        preview = self.findNavigation(QPreview)
        if preview:
            self.setWindowTitle(f'Connected: {preview.ipAddress.text()}')
        else:
            self.setWindowTitle('Not connected')

    @pyqtSlot()
    def onPopNavigationStack(self):
        if len(self.navigation) > 1:
            for i in self.navigation:
                self.Client.layout().removeWidget(i)
                i.hide()
           
            self.navigation.pop(len(self.navigation) - 1)

            current = self.navigation[len(self.navigation) - 1]
            self.Client.layout().addWidget(current);
            current.show()
        
        self.back.setEnabled(len(self.navigation) > 1)
        
    def findNavigation(self, widgetType):
        return [widget for widget in self.navigation if isinstance(widget, widgetType)][0]
    
    def onConnect(self, ipaddr):
        self.findNavigation(QPreview).onConnect(ipaddr)
        self.onPopNavigationStack()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QMainWnd()
    widget.show()
    sys.exit(app.exec_())
