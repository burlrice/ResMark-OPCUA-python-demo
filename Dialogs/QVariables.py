from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QTableWidget, QWidget
from PyQt5.uic import loadUi

from .path import resolveUi
from message import Message

class QVariables(QDialog):
    def __init__(self, parent: QWidget, message: Message):
        super().__init__(parent)
        loadUi(resolveUi('variables.ui'), self)

        self.table = self.findChildren(QTableWidget, 'tableWidget')[0];
        self.table.setColumnCount(1)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft);
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        for i in message.counts:
            print(i)

    def setVisible(self, visible: bool):
        super().setVisible(visible)
        #self.listWidget.addItems(self.messages)
