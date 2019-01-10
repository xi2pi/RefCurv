# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas


import os
import subprocess
import pandas as pd
import numpy as np
import sys

from helprefcurv import *

class AdModelFitting(QtGui.QDialog):    
    def __init__(self, mainWindow):
        super(AdModelFitting, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.gamlss_model = "gamlss(y ~ pb(x, df = 1), sigma.formula = ~ pb(x, df = 0), nu.formula = ~pb(x, df = 0), family = \"BCCG\", method = RS(), data = data_perc)"
            
        
        self.createFormGroupBox()

        self.chosen_xAxis = "none"
        self.chosen_yAxis = "none"
        
        self.command = 'Rscript'
        
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
        
        self.resize(500, 300)
        
        self.outPut = QtGui.QTextEdit()

        
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.compute_refcurv)
        self.buttonBox.rejected.connect(self.reject)
 
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.outPut)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)
        
        self.mainW = mainWindow
        
    
    def createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("GAMLSS")
        layout = QtGui.QFormLayout()
        
        self.gamlss_textfield = QtGui.QLineEdit()
        self.gamlss_textfield.setText(self.gamlss_model)
        layout.addRow(QtGui.QLabel("Input: "), self.gamlss_textfield)

        
        self.formGroupBox.setLayout(layout)
        
    def compute_refcurv(self):
        self.outPut.clear()
        self.mainW.refcurv_computed = False
        self.mainW.plot_data()
        self.mainW.canvas.draw()
        
        try:
            os.remove(self.program_path + "/tmp/percentiles_chart.csv")
        except:
            print("no ./tmp/percentiles_chart.csv to remove")

        
        path2script = self.program_path + '/R_model/perc_model_flexible.R'

        # Smoothing parameter
        args = ['1', '0', '0']
        
        self.gamlss_model = self.gamlss_textfield.text()
        print(self.gamlss_model)
        
        args_digit = [entry_text for entry_text in args if entry_text.isdigit()]
        
        if len(args_digit) == 3:
            points_on = "TRUE"
            
            self._process = QtCore.QProcess(self)
            self._process.readyReadStandardOutput.connect(self.processOutput)
            self._process.finished.connect(self.processFinished)
            
            self.popUp = PopUpProcess(self)
            
        
            if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
                fileName = [self.program_path +"/tmp/cur_data.csv"]
                config = [self.chosen_xAxis, self.chosen_yAxis, points_on, self.gamlss_model]
                command_arg = [path2script] + args + fileName + config
                try:
                    self._process.start(self.command, command_arg, QtCore.QIODevice.ReadOnly)
                    self.popUp.onStart()
                    self.popUp.show()
                except:
                    print("process error")
                    self.outPut.setText("process error")
            else:
                print("no data")
        else:
            print("no integer in text field")
        
    def processOutput(self):
         self.outPut.append(str(self._process.readAllStandardOutput(), encoding = "utf-8"))
            
    def processFinished(self):
        print("finished") 
        if os.path.isfile(self.program_path +"/tmp/percentiles_chart.csv"):
            self.mainW.refcurv_computed = True
            self.mainW.plotButton.setEnabled(False)
            self.mainW.xCombo.setEnabled(False)
            self.mainW.yCombo.setEnabled(False)
            self.mainW.disable_table()
            self.mainW.plot_data()
            self.mainW.mark_outlier()
            self.popUp.onFinished()
            self.popUp.close()
            self.fittingFinishedWindow()

        else:
            print("model fitting error")
            self.popUp.onFinished()
            self.popUp.close()
            self.errorWindow()
    
        
        
    def fittingFinishedWindow(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        msgBox.setText("The model fitting was successful!")
        msgBox.setWindowTitle("Model Fitting")
        msgBox.setDetailedText("Model parameters: \n" + self.gamlss_model)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msgBox.exec_()
            
    def errorWindow(self):
        msgBox = QtGui.QMessageBox.critical(
            self,
            "ERROR",
            "The model could not be fitted")
    

        

            

