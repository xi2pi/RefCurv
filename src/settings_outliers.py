# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os

class OutliersSettings(QtGui.QDialog):
    NumGridRows = 3
    NumButtons = 4
 
    def __init__(self, mainWindow):
        super(OutliersSettings, self).__init__()
        
        self.outlier_on_off = False
        self.outlier_limit_up = 99
        self.outlier_limit_low = 1
        
        
        self.createFormGroupBox()
        
        self.setWindowIcon(QIcon(os.getcwd() +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
 
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(mainWindow.set_Outlier)
        buttonBox.rejected.connect(self.reject)
 
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

 
    def createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Settings")
        layout = QtGui.QFormLayout()
        
        self.outlier_on = QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("Outliers detection (on/off): "), self.outlier_on)
        self.outlier_limit_up_edit = QtGui.QLineEdit()
        self.outlier_limit_up_edit.setText(str(self.outlier_limit_up))
        layout.addRow(QtGui.QLabel("Outliers Limit (up) [%]: "), self.outlier_limit_up_edit)
        self.outlier_limit_low_edit = QtGui.QLineEdit()
        self.outlier_limit_low_edit.setText(str(self.outlier_limit_low))
        layout.addRow(QtGui.QLabel("Outliers Limit (low) [%]: "), self.outlier_limit_low_edit)
        self.formGroupBox.setLayout(layout)
        
