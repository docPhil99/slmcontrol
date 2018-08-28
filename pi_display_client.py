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
import sys,os
import requests
from PyQt4 import QtCore as qtcore
import base64
import numpy as np
from PIL import Image

HOST ='http://192.168.2.50:12345'

ENCODING = 'utf-8'


class make_test_pattern():
    def __init__(self,width,height,num,max_val=255):
        self.width=width
        self.height=height
        self.max_val=max_val
        self.num=num
        xx = np.linspace(0,2*np.pi,width)
        yy=np.linspace(0,2*np.pi,height)
        self.XX,YY=np.meshgrid(xx,yy)
        self._c=1

    def __iter__(self):
        return self
    def __next__(self):
    
        data=(np.sin(0.5*self.XX*self._c*self.width/self.num)+1)*self.max_val/2
        self._c+=1
        if self._c>self.num:
            self._c=1
        return data
    
    

        

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.ipaddress = QtGui.QLineEdit()
        self.filename = QtGui.QLineEdit()
        self.ipaddress.setInputMask("000.000.000.000;_")
        self.port = QtGui.QLineEdit()
        self.port.setValidator(QtGui.QIntValidator())
        self.button = QtGui.QPushButton('Send', self)
        self.button.clicked.connect(self.handleButton)
        self.button2 = QtGui.QPushButton('Quit', self)
        self.button2.clicked.connect(self.handleButton2)
        self.button3 = QtGui.QPushButton('Get info', self)
        self.button3.clicked.connect(self.handleButton3)
        self.button4 = QtGui.QPushButton('Demo', self)
        self.button4.clicked.connect(self.run_demo)
        self.textbox=QtGui.QTextEdit()
        
        self.textbox.setReadOnly(True)
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(QtGui.QLabel("IP address"))
        
        layout.addWidget(self.ipaddress)
        layout.addWidget(QtGui.QLabel("Port"))
        layout.addWidget(self.port)
        layout.addWidget(QtGui.QLabel("File"))
        lay2=QtGui.QHBoxLayout(self)
        self.filebut=QtGui.QPushButton('...', self)
        self.filebut.clicked.connect(self._get_file)
        lay2.addWidget(self.filename)
        lay2.addWidget(self.filebut)
        layout.addLayout(lay2)
        layout.addWidget(self.button)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.button2)
        layout.addWidget(self.textbox)
        self.last_msg=''
        self.timer=None
        self.array_get=None
        #self.load_data('/Volumes/LocalDataHD/engg/engg/tafj0/Google Drive/Matlab/images/lena.tif')
        self.load_settings()
        
    def _get_file(self):
        fname=QtGui.QFileDialog.getOpenFileName(self,'Send file',os.getcwd(),"Images (*.png *.bmp *.jpg)")
        self.filename.setText(fname)
        
    def load_settings(self):
        try:
            with open('settings.json') as f:
                self.settings=json.load(f)
        except:
            self.settings={'ip':'192.168.2.50','port':'12345','file':'test.png'}
            self.save_settings(from_gui=False)
        self.ipaddress.setText(self.settings['ip'])
        self.port.setText(self.settings['port'])
        self.filename.setText(self.settings['file'])
    def save_settings(self,from_gui=True):
        if from_gui==True:
            #update settinds from gui
            self.settings['port']=self.port.text()
            self.settings['ip']=self.ipaddress.text()
            self.settings['file']=self.filename.text()
            
        with open('settings.json','wt') as f:
            json.dump(self.settings,f)
    def load_data(self,filename):
        
        self.data={'command':'display','image':None}
        #pixmap = QtGui.QPixmap()
        #if pixmap.load(filename)==0:
        #    print('Cannot load file {}'.format(filename))
        with open(filename,'rb') as file:
            self.data['image']=base64.b64encode(file.read()).decode(ENCODING)
    def _send_data(self,data):
        host= "http://{}:{}".format(self.settings['ip'],self.settings['port'])
        print('Sending data to {}'.format(host))
        try:
            r=requests.post(host, data)
            r.raise_for_status()
        except Exception as e:
            self.textbox.append("Exceptions: {}".format(str(e)))
        print(r.status_code) 
        self.textbox.append("Status code: {}".format(r.status_code))
        self.textbox.append(r.text)
        self.last_msg=r.text
       
    def run_demo(self):
        if self.button4.text()=='Demo':
            data=json.dumps({'command':'info'})
            self._send_data(data)
            print('Last msg= {}'.format(self.last_msg))
            j=json.loads(self.last_msg)
            print(j)
            self.array_get=make_test_pattern(j['width'],j['height'],4)
            self.timer=qtcore.QTimer()
            self.timer.timeout.connect(self._run_demo)
            self.timer.start(1000)
            self.button4.setText('Stop')
        else:
            self.timer.stop()
            self.button4.setText('Demo')
    def _run_demo(self):
        data=next(self.array_get)
        temp = BytesIO()
        im = Image.fromarray(data.astype(np.uint8))
        im.save(temp, format="png")
        im.save('test.png')
        self.data={'command':'display','image':None}
        #self.data['image']=base64.b64encode(temp.read()).decode(ENCODING)
        self.data['image']=base64.b64encode(temp.getvalue()).decode(ENCODING)
        jdata=json.dumps(self.data)
        
        self._send_data(jdata)
        
    def handleButton(self):
        self.save_settings()
        self.load_data(self.settings['file'])
        data=json.dumps(self.data)
        #print(data)
        self._send_data(data)
    def handleButton2(self):
        self.save_settings()
        data=json.dumps({'command':'quit'})
        #print(data)
        self._send_data(data)    
    def handleButton3(self):
        self.save_settings()
        data=json.dumps({'command':'info'})
        #print(data)
        self._send_data(data)    
    def closeEvent(self, event):
        self.save_settings()
        
        #self.httpd.stop()

if __name__ == '__main__':
    app=0
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

