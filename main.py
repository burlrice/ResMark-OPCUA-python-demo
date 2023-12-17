import sys
import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QMenu, QToolButton, QPushButton
from PyQt5.uic import loadUi

from Dialogs.QSearch import QSearch
from Dialogs.QPreview import QPreview

class QMainWnd(QMainWindow):
    
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'form.ui'), self)
        self.navigation = []
        
        self.back = self.centralWidget().findChildren(QPushButton, 'back')[0];
        self.back.clicked.connect(lambda: self.popNavigationStack())
           
        self.pushNavigationStack(QPreview())
        self.pushNavigationStack(QSearch())

    def pushNavigationStack(self, widget):
        for i in self.navigation:
            self.Client.layout().removeWidget(i)
            
        self.navigation.append(widget)
        self.Client.layout().addWidget(self.navigation[len(self.navigation) - 1]);
        self.back.setEnabled(len(self.navigation) > 1)

    def popNavigationStack(self):
        if len(self.navigation) > 1:
            for i in self.navigation:
                self.Client.layout().removeWidget(i)
                
            self.navigation.pop(len(self.navigation) - 1)
            self.Client.layout().addWidget(self.navigation[len(self.navigation) - 1]);
        
        self.back.setEnabled(len(self.navigation) > 1)

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QMainWnd()
    widget.show()
    sys.exit(app.exec_())
