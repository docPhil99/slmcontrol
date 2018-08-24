#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 12:48:56 2018

@author: tafj0
"""

from http.server import HTTPServer, BaseHTTPRequestHandler#, SimpleHTTPRequestHandler
from PyQt4 import QtCore, QtGui
from io import BytesIO
import json
import sys
import requests
from PyQt4 import QtCore as qtcore
import base64
HOST ='http://127.0.0.1:12345'

ENCODING = 'utf-8'


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.button = QtGui.QPushButton('Send', self)
        self.button.clicked.connect(self.handleButton)
        self.button2 = QtGui.QPushButton('Quit', self)
        self.button2.clicked.connect(self.handleButton2)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        self.load_data('/Volumes/LocalDataHD/engg/engg/tafj0/Google Drive/Matlab/images/lena.tif')
       
    def load_data(self,filename):
        self.data={'command':'display','image':None}
        #pixmap = QtGui.QPixmap()
        #if pixmap.load(filename)==0:
        #    print('Cannot load file {}'.format(filename))
        with open(filename,'rb') as file:
            self.data['image']=base64.b64encode(file.read()).decode(ENCODING)
    def handleButton(self):
        data=json.dumps(self.data)
        #print(data)
        r=requests.post(HOST, data)
        print(r.status_code)
    def handleButton2(self):
        data=json.dumps({'command':'quit'})
        #print(data)
        r=requests.post(HOST, data)
        print(r.status_code)       
    def closeEvent(self, event):
        pass
        #self.httpd.stop()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

