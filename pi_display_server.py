#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 14:44:56 2018

@author: tafj0
"""

import sys
import base64

from http.server import HTTPServer, BaseHTTPRequestHandler#, SimpleHTTPRequestHandler
from PyQt4 import QtCore, QtGui
from PyQt4 import Qt
from io import BytesIO
import inspect
import json
from PyQt4 import QtCore as qtcore
HOST, PORT = '', 12345


class Settings:
    width=1
    height=1
    @classmethod
    def to_json(cls):

        w={key:value for key, value in cls.__dict__.items() if not
                key.startswith('__') and not callable(value) and not
                key=="update" and not key=="to_json"}
        r=json.dumps(w)
        return r
    @classmethod
    def update(cls):

        rect=QtGui.QApplication.desktop().screenGeometry()
        cls.width=rect.width()
        cls.height=rect.height()
        w={key:value for key, value in cls.__dict__.items() if not
                key.startswith('__') and not callable(value) and not
                key=="update" and not key=="to_json"}
        print(w)
#        print(json.dumps(w))


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        
        self.end_headers()
        #print(body)
        data=json.loads(body.decode('utf-8'))
 #       print(data)
        #self.emit(qtcore.SIGNAL("signal"),json)
        r=self.server._got_data(data)
        response = BytesIO()
        #response.write(b'from slmcontrol server: ')
        response.write(str.encode(r))
        self.wfile.write(response.getvalue())
class myServer(HTTPServer):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        super().__init__(*args,**kwargs)

    def _got_data(self,data):
        print('got data')
        if data['command']=='info':
            r=Settings.to_json()
        else:
            r=data['command']
            self.parent.got_data(data)
        return r
        
    
class HttpDaemon(QtCore.QThread):
    data_signal= qtcore.pyqtSignal(dict)
    
    def got_data(self,data):
        
        
        self.data_signal.emit(data)
        
    def __init__(self,*args,**kwargs):
        self.server=None
        super().__init__(*args,**kwargs)
        
        
    def run(self):
        self.server = myServer(self,(HOST, PORT), SimpleHTTPRequestHandler)
        self.data_signal.emit({'command':'running server'})
        self.server.serve_forever()
    
        
    def stop(self):
        self.server.shutdown()
        self.server.socket.close()
        self.wait()

class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        Settings.update()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        styleSheetCss="QWigget {border-width: 0px;}"
        self.setStyleSheet(styleSheetCss)
        self.showFullScreen()
        self.resize(800,480)
        self.image_label=QtGui.QLabel("image")
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.setContentsMargins(0,0,0,0)
        self.httpd = HttpDaemon(self)
        self.httpd.start()
        self.httpd.data_signal.connect(self.handleJSON)
        self.setCursor(qtcore.Qt.BlankCursor) 
        
    @qtcore.pyqtSlot(str)
    def handleJSON(self,data):
        print('handleJSON')
        command=data['command']
        print(command)
        if command=='quit':
            self.close()
            sys.exit(0)
        if command=='display':
            image_file_data=base64.b64decode(data['image'])
            pix=QtGui.QPixmap()
            pix.loadFromData(image_file_data)
            self.image_label.setPixmap(pix)

    def closeEvent(self, event):
        self.httpd.stop()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
