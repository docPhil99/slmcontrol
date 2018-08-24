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
from io import BytesIO
import json
from PyQt4 import QtCore as qtcore
HOST, PORT = '127.0.0.1', 12345

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
        
        data=json.loads(body.decode('utf-8'))
        #print(data)
        #self.emit(qtcore.SIGNAL("signal"),json)
        self.server._got_data(data)
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())
class myServer(HTTPServer):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        super().__init__(*args,**kwargs)
        
    def _got_data(self,data):
        
        print('got data')
        self.parent.got_data(data)
        
    
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

        self.showFullScreen()
        self.image_label=QtGui.QLabel("image")
        layout = QtGui.QVBoxLayout(self)
       
        layout.addWidget(self.image_label)
        self.httpd = HttpDaemon(self)
        self.httpd.start()
        self.httpd.data_signal.connect(self.handleJSON)
       
        
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
        
        #self.button.setText(data)
        

    
    def closeEvent(self, event):
        self.httpd.stop()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
