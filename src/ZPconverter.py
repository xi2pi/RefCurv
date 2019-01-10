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
import sys
#import shutil

import scipy.stats as st


class ZP_converter(QtGui.QMainWindow):    
    def __init__(self, parent=None):
        super(ZP_converter, self).__init__()  
        self.program_path = os.path.dirname(sys.argv[0])           
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.hLayout = QtGui.QHBoxLayout()
        self.mainLayout.insertLayout(1, self.hLayout)
        
        self.setGeometry(50, 50, 500, 500)
        
        self.p2z_convert_flag = True
        
        self.b1 = QtGui.QRadioButton("Percentile -> Z-Score")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
        self.mainLayout.addWidget(self.b1)
		
        self.b2 = QtGui.QRadioButton("Z-Score -> Percentile")
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
          
        self.mainLayout.addWidget(self.b2)
                
        
#        okButton = QtGui.QPushButton("Ok")
#        okButton.clicked.connect(self.calc_zscore)
        
        #self.buttonBox = QtGui.QDialogButtonBox(okButton | QtGui.QDialogButtonBox.Cancel)
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.convert_value)
        
        self.init_createFormGroupBox()
        
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.widget_btns)

        
    def init_createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Z-score/Percentile")
        
        self.val_entry = QtGui.QLineEdit()
        self.val_label = QtGui.QLabel()
        
        self.val_entry.setText("50")
        self.val_label.setText("0")
        
        self.name_entry = QtGui.QLabel("Percentile [%]:")
        self.name_label = QtGui.QLabel("Z-Score [-]:")
        
        layout = QtGui.QFormLayout()
        layout.addRow(self.name_entry, self.val_entry)
        layout.addRow(self.name_label, self.val_label)
        self.formGroupBox.setLayout(layout)
        
    def z_score(self, L, M, S, y):
        if L == 0:
            z = (1/S)*np.log(y/M)
        else:
            z = (1/(S*L))*(((y/M)**L)-1)
        return z
        
    def p2z(self, value):
        return st.norm.ppf(value)
        
    def z2p(self, value):
        return st.norm.cdf(value)
        
    def convert_value(self):
        if self.p2z_convert_flag == True:
            self.val_label.setText(str(round(self.p2z(float(self.val_entry.text())/100), 5)))
        else:
            self.val_label.setText(str(round(self.z2p(float(self.val_entry.text())), 5)*100))
        
    def btnstate(self,b):
      if b.text() == "Percentile -> Z-Score":
         if b.isChecked() == True:
            self.p2z_convert_flag = True
            self.name_entry.setText("Percentile [%]:")
            self.name_label.setText("Z-Score [-]:")
         else:
            print("deselected")
            #self.p2z_convert_flag = False
				
      if b.text() == "Z-Score -> Percentile":
         if b.isChecked() == True:
            self.p2z_convert_flag = False
            self.name_entry.setText("Z-Score [-]:")
            self.name_label.setText("Percentile [%]:")
         else:
             print("deselected")
            #self.p2z_convert_flag = False
        
        
        
 
            
            
        

        


