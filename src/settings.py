# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *


import os

class PlotSettings(QtGui.QDialog):
    NumGridRows = 3
    NumButtons = 4
 
    def __init__(self, parent=None):
        super(PlotSettings, self).__init__()
        self.createFormGroupBox()
        
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
 
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
 
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
	

 
    def createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Settings")
        layout = QtGui.QFormLayout()
        
        points_shown = QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("Points (on/off): "), points_shown)
        grid_shown = QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("Grid (on/off): "), grid_shown)
        label_shown = QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("Label reference curves (on/off): "), label_shown)
        p_label_size = QtGui.QLineEdit()
        layout.addRow(QtGui.QLabel("Label size (Reference Curves): "), p_label_size)
#        layout.addRow(QtGui.QLabel("Name:"), QtGui.QLineEdit())
#        layout.addRow(QtGui.QLabel("Country:"), QtGui.QComboBox())
#        layout.addRow(QtGui.QLabel("Age:"), QtGui.QSpinBox())
        self.formGroupBox.setLayout(layout)