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

class ModelFitting(QtGui.QDialog):    
    def __init__(self, mainWindow):
        super(ModelFitting, self).__init__() 
        #self.program_path = os.path.dirname(sys.argv[0])
        self.program_path = os.getcwd()

        self.chosen_xAxis = "none"
        self.chosen_yAxis = "none"
        
        self.command = 'Rscript'
        
        # GUI
        self.createFormGroupBox()        
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
        self.formGroupBox = QtGui.QGroupBox("Smoothing Parameter")
        layout = QtGui.QFormLayout()
        
        self.Mu_textfield = QtGui.QLineEdit()
        self.Mu_textfield.setText("1")
        layout.addRow(QtGui.QLabel("M_df: "), self.Mu_textfield)
        self.Sigma_textfield = QtGui.QLineEdit()
        self.Sigma_textfield.setText("0")
        layout.addRow(QtGui.QLabel("S_df: "), self.Sigma_textfield)
        self.Lambda_textfield = QtGui.QLineEdit()
        self.Lambda_textfield.setText("0")
        layout.addRow(QtGui.QLabel("L_df"), self.Lambda_textfield)
        self.Lambda_textfield.setFixedWidth(30)
        self.Sigma_textfield.setFixedWidth(30)
        self.Mu_textfield.setFixedWidth(30)
        
        self.formGroupBox.setLayout(layout)
        
    # compute the reference curves by model fitting
    def compute_refcurv(self):
        self.outPut.clear()
        self.mainW.refcurv_computed = False
        self.mainW.plot_data()
        self.mainW.canvas.draw()
        
        try:
            os.remove(self.program_path + "/tmp/percentiles_chart.csv")
        except:
            print("no ./tmp/percentiles_chart.csv to remove")

        # path to the R script for model fitting
        path2script = self.program_path + '/R_model/perc_model_flexible.R'
        
        # Smoothing parameter
        args = ['1', '0', '0']
        args[0] = self.Mu_textfield.text()
        args[1] = self.Sigma_textfield.text()
        args[2] = self.Lambda_textfield.text()
        
        # digitalizing strings
        args_digit = [entry_text for entry_text in args if entry_text.isdigit()]
        
        if len(args_digit) == 3:
            points_on = "TRUE"
            
            # Starting the computation process
            self._process = QtCore.QProcess(self)
            self._process.readyReadStandardOutput.connect(self.processOutput)
            self._process.finished.connect(self.processFinished)
            
            self.popUp = PopUpProcess(self)
            
            # defining the model
            self.gamlss_model = "gamlss(y ~ pb(x, df = median_df), sigma.formula = ~ pb(x, df = sigma_df), nu.formula = ~pb(x, df = nu_df), family = \"BCCG\", method = RS(), data = data_perc)"
            
            if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
                fileName = [self.program_path +"/tmp/cur_data.csv"]
                config = [self.chosen_xAxis, self.chosen_yAxis, points_on, self.gamlss_model]
                command_arg = [path2script] + args + fileName + config
                print("-----------")
                print(command_arg)
                try:
                    self._process.start(self.command, command_arg, QtCore.QIODevice.ReadOnly)
                    print("R script: " + self.command)
                    print("model fitting script: " + path2script)
                    self.popUp.onStart()
                    self.popUp.show()
                except:
                    print("process error")
                    self.outPut.setText("process error")
            else:
                print("no data")
        else:
            print("no integer in text field")
            self.errorWindow()
       
    # process output
    def processOutput(self):
         self.outPut.append(str(self._process.readAllStandardOutput(), encoding = "utf-8"))
        
    # after process finished
    def processFinished(self):
        print("finished") 
        if os.path.isfile(self.program_path + "/tmp/percentiles_chart.csv"):
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
    
    # showing results in a popup window 
    def fittingFinishedWindow(self):
        M_edf = "e.d.f. M = " + self.Mu_textfield.text() + "\n"
        S_edf = "e.d.f. S = " + self.Sigma_textfield.text() + "\n"
        L_edf = "e.d.f. L = " + self.Lambda_textfield.text() 
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        msgBox.setText("The model fitting was successful!")
        msgBox.setWindowTitle("Model Fitting")
        msgBox.setDetailedText("Model parameters: \n" + M_edf + S_edf + L_edf)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msgBox.exec_()
           
    # error handling
    def errorWindow(self):
        msgBox = QtGui.QMessageBox.critical(
            self,
            "ERROR",
            "The model could not be fitted")
    

        

            

