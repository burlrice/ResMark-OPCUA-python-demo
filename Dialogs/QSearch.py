import os
import re
import socket
import select
import threading

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QPushButton, QTableWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QMovie, QPixmap

from .path import resolveUi, resolveImage
from printer import Printer

class QSearch(QtWidgets.QDialog):
    printerDetected = pyqtSignal(str, str)
    
    def __init__(self, connect): # TODO: drop connect, use resolveTopMostWidget
        super().__init__()
        loadUi(resolveUi('search.ui'), self)

        self.connect = connect
        
        self.refresh = self.findChildren(QPushButton, 'refresh')[0];
        self.refresh.clicked.connect(self.onRefresh)
        self.printers = {}
        self.onRefresh()
        
        self.table = self.findChildren(QTableWidget, 'tableWidget')[0];
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Address', 'Name', ''])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft);
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.printerDetected.connect(self.addPrinter)

    def onRefresh(self):
        self.refresh.setEnabled(False)

        self.refreshIcon = self.refresh.icon()

        self.movie = QMovie(resolveImage('Refresh.gif'))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start();
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.onRefreshComplete)
        self.timer.start(2000)
        self.thread = threading.Thread(target=self.broadcast)
        self.thread.start()        

    def broadcast(self):
        addr = socket.gethostbyname(socket.gethostname())
        
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp.bind((addr, 1706))
        udp.sendto(b'{Locate LCIJTask1}', ('255.255.255.255', 2201))
        
        while(self.timer.isActive()):
            readable, _, _ = select.select([udp], [], [], .250) 
            for sock in readable:
                data, address = udp.recvfrom(1024)
                self.printerDetected.emit(address[0], data.decode())
                
        udp.close()
        
    def onRefreshComplete(self):
        self.refresh.setIcon(self.refreshIcon)
        self.timer.stop()
        self.movie.stop()
        self.refresh.setEnabled(True)
        
    def onFrameChanged(self):
        self.refresh.setIcon(QIcon(self.movie.currentPixmap()))

    @pyqtSlot(str, str)
    def addPrinter(self, addr, data):
        self.printers[addr] = data

        index = len(self.printers) - 1
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item != None and item.text() == addr:
                index = row
                break
        
        self.table.setRowCount(len(self.printers))
        
        name = re.search(r'Head Name=([^,]+)', data)
        
        self.table.setCellWidget(index, 0, QLabel(addr))
        self.table.setCellWidget(index, 1, QLabel(name.group(1) if name else data))
        connect = QPushButton()
        icon = QIcon(resolveImage('connect.png'))
        connect.setIcon(icon)
        connect.setIconSize(QSize(24, 24))
        connect.clicked.connect(self.onConnect)
        self.table.setCellWidget(index, 2, connect)

    @pyqtSlot()
    def onConnect(self):
        for i in self.table.selectedIndexes():
            try:
                addr = self.table.cellWidget(i.row(), 0).text()
                printer = Printer(addr)
                if printer.GetStatusInformation() != None:
                    self.connect.emit(addr)
                    break
            except Exception as e:
                print(e)
                    