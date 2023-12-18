import os
import re
import socket
import select
import threading
from tkinter import SE

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QIcon, QMovie, QPixmap

from .path import resolveUi, resolveImage

class QSearch(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        loadUi(resolveUi('search.ui'), self)

        self.refresh = self.findChildren(QPushButton, 'refresh')[0];
        self.refresh.clicked.connect(self.onRefresh)
        self.printers = {}
        self.onRefresh()
        
    def onRefresh(self):
        self.refresh.setEnabled(False)

        self.icon = self.refresh.icon()

        self.movie = QMovie(resolveImage('Refresh.gif'))
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start();
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.stop_animation)
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
                self.printers[address[0]] = data.decode()
                print(self.printers)
                
        udp.close()
        
    def stop_animation(self):
        self.refresh.setIcon(self.icon)
        self.timer.stop()
        self.movie.stop()
        self.refresh.setEnabled(True)
        
    def onFrameChanged(self):
        self.refresh.setIcon(QIcon(self.movie.currentPixmap()))

