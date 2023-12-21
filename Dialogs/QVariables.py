from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QHeaderView, QLabel, QLineEdit, QPushButton, QTableWidget, QTextEdit, QWidget
from PyQt5.uic import loadUi

from printer import Printer
from .path import resolveTopMostWidget, resolveUi
from message import Message

class QVariables(QDialog):
    def __init__(self, printer: Printer, message: Message, printPreview: pyqtSignal):
        super().__init__()
        loadUi(resolveUi('variables.ui'), self)

        self.printer = printer
        self.message = message
        self.printPreview = printPreview
        
        self.findChildren(QPushButton, 'start')[0].clicked.connect(self.onStart)
        self.findChildren(QPushButton, 'cancel')[0].clicked.connect(self.onCancel)

        self.table = self.findChildren(QTableWidget, 'tableWidget')[0];
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Type', 'Value'])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 150)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft);
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.table.setRowCount(len(message.counts) + len(message.variables) + len(message.dataSet))
        
        index = 0
        for i in message.counts:
            txt = QLineEdit()
            txt.setText(i)
            self.table.setCellWidget(index, 0, QLabel('Count'))
            self.table.setCellWidget(index, 1, txt)
            index += 1
        
    def setVisible(self, visible: bool):
        super().setVisible(visible)

        if visible:
            txt = self.table.cellWidget(0, 1);
            txt.setFocus()
            txt.selectAll()

    def onStart(self):
        main = resolveTopMostWidget(self)
        variables = dict()
        
        for i in range(0, self.table.rowCount()):
            label = self.table.cellWidget(i, 0).text()
            
            if label == 'Count':
                variables['Count'] = self.table.cellWidget(i, 1).text()
            
        main.onPopNavigationStack()
    
        if 'Count' in variables and len(variables) == 1:
            self.printer.PathPrintStoredMessage('', self.message.name)
            self.printer.SetMessageCount(int(variables['Count']))
            self.printPreview.emit()
        else:
            print('TODO: other variables')

            
    def onCancel(self):
        resolveTopMostWidget(self).onPopNavigationStack()
        