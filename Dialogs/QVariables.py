import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Type', 'Value', ''])
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
            txt.setValidator(QIntValidator())
            txt.returnPressed.connect(self.onReturnPressed)
            self.table.setCellWidget(index, 0, QLabel('Count'))
            self.table.setCellWidget(index, 1, txt)
            self.table.setCellWidget(index, 2, QLabel()) # unique from possible DataSet column name 'Count'
            index += 1

        for i in message.dataSet:
            txt = QLineEdit()
            txt.setText(message.dataSet[i])
            txt.returnPressed.connect(self.onReturnPressed)
            self.table.setCellWidget(index, 0, QLabel(i))
            self.table.setCellWidget(index, 1, txt)
            index += 1
        
    def setVisible(self, visible: bool):
        super().setVisible(visible)

        if visible:
            txt = self.table.cellWidget(0, 1);
            txt.setFocus()
            txt.selectAll()

    def getIndex(self, label: QLineEdit) -> int:
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 1) == label:
                return i
        
        return -1
    
    def onReturnPressed(self):
        index = self.getIndex(self.sender())
        print(index, self.table.rowCount())
        
        if (index < (self.table.rowCount() - 1)):
            txt = self.table.cellWidget(index + 1, 1);
            txt.setFocus()
            txt.selectAll()
        else:
            self.onStart()
        
    def onStart(self):
        main = resolveTopMostWidget(self)
        variables = dict()
        
        for i in range(self.table.rowCount()):
            label = self.table.cellWidget(i, 0).text()
            
            if label == 'Count' and self.table.cellWidget(i, 2) != None:
                variables['Count'] = self.table.cellWidget(i, 1).text()
            else:
                variables[self.table.cellWidget(i, 0).text()] = self.table.cellWidget(i, 1).text()
            
        main.onPopNavigationStack()
    
        if 'Count' in variables and len(variables) == 1:
            self.printer.PathPrintStoredMessage('', self.message.name)
            time.sleep(1)
            self.printer.SetMessageCount(int(variables['Count']) - 1)
            self.printPreview.emit()
        else:
            for i in self.message.document.xpath('//ProductObject//Variables//DataSet//ColumnValues//Column'):
                if 'Value' in i.attrib:
                    i.attrib['Value'] = variables[i.attrib['Name']]
                    
            self.printer.PrintMessage(str(self.message))
    
            if 'Count' in variables:
                self.printer.SetMessageCount(int(variables['Count']))

            
    def onCancel(self):
        resolveTopMostWidget(self).onPopNavigationStack()
        