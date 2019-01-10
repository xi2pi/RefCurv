# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import os

''' About window '''
class AboutWindow(QtGui.QDialog):
    def __init__(self):        
        super(AboutWindow, self).__init__()
        self.program_path = os.path.dirname(sys.argv[0])
        
        
        self.splitter = QtGui.QSplitter()
        self.pic_label = QtGui.QLabel()
        self.center()        
        
        # logo
        self.pic = QtGui.QPixmap(self.program_path + "/logo/refcurv_logo.png")
        self.pic_resized = self.pic.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        
        self.pic_label.setPixmap(self.pic_resized)
        self.pic_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # author
        self.label_author = QtGui.QLabel("RefCurv")
        self.label_author.setAlignment(QtCore.Qt.AlignCenter)
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
        

        self.mainlayout = QtGui.QVBoxLayout()
        self.mainlayout.addWidget(self.pic_label)
    
    # set the version
    def set_version(self, rc_version):      
        self.label_author = QtGui.QLabel("RefCurv \n " + rc_version + " \nCopyright © 2018 Christian Winkler")
        self.mainlayout.addWidget(self.label_author)
        self.label_author.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainlayout)   
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

''' Popup window for progress during model fitting '''        
class PopUpProcess(QtGui.QMainWindow):
    def __init__(self, parent= None):
        super(PopUpProcess, self).__init__()
        self.program_path = os.path.dirname(sys.argv[0])
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        self.setWindowTitle("Processing...")
        
        self.resize(300, 100)
        self.center()
        
        self.initUI()
        
    def initUI(self):     
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        
        # main orientation is horizontal
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setRange(0,1)
        self.mainLayout.addWidget(self.pbar)
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
        
    def onStart(self): 
        self.pbar.setRange(0,0)
    def onFinished(self):
        self.pbar.setRange(0,1)
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
        
        

