# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import os
import pandas as pd
import numpy as np

from scipy import interpolate
from scipy.stats import truncnorm

class r_path(QtGui.QMainWindow):   


    def __init__(self, mainWindow, modelFitter, modelselect, modelselectCV, sensiti, adfitting):
        super(r_path, self).__init__() 
        self.program_path = mainWindow.program_path
        
        self.fitter = modelFitter
        self.modelselect = modelselect
        self.modelselectCV = modelselectCV
        self.sensiti = sensiti
        self.adfitter = adfitting
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowTitle('RefCurv 0.3.0 - R path')
        self.setWindowIcon(QIcon(os.getcwd() +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.hLayout = QtGui.QHBoxLayout()
        self.mainLayout.insertLayout(1, self.hLayout)
        
        self.resize(500, 100)
        self.center_window()
                
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.set_new_path)
        
        self.init_createFormGroupBox()
        
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.widget_btns)
        
        self.init_path()
        
    def init_path(self):
        R_path = self.program_path + '/R-3.3.2/bin/Rscript'
        self.fitter.command = R_path
        self.modelselect.command = R_path
        self.modelselectCV.command = R_path
        self.adfitter.command = R_path
        self.sensiti.command = R_path
    
        
    def init_createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("R Path")
        
        self.path_entry = QtGui.QLineEdit()
        
        self.path_entry.setText(self.fitter.command)
        
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel("R path:"), self.path_entry)
        self.formGroupBox.setLayout(layout)
        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def set_new_path(self):
        self.fitter.command = self.path_entry.text()
        self.modelselect.command = self.path_entry.text()
        self.modelselectCV.command = self.path_entry.text()
        self.adfitter.command = self.path_entry.text()
        self.sensiti.command = self.path_entry.text()
        
        self.close()
        
        

        


