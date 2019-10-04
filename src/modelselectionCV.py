from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from functools import partial
import subprocess
import os
import sys


class ModelSelectionCV(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ModelSelectionCV, self).__init__()
        self.program_path = os.path.dirname(sys.argv[0])

        self.setWindowIcon(QIcon(self.program_path  +'/logo/refcurv_logo.png'))
        
        self.x_value = None
        self.y_value = None
        
        self.fileName = None
        
        self.command = self.program_path + '/Rscript'
        
        self.setGeometry(50, 50, 500, 300)
        self.setupUI()

    def setupUI(self):
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        layout = QtGui.QGridLayout()
       
        # Labels
        self.MuRange = QtGui.QLabel("M")
        layout.addWidget(self.MuRange, 0, 0)  
        self.SigmaRange = QtGui.QLabel("S")
        layout.addWidget(self.SigmaRange, 1, 0) 
        self.LambdaRange = QtGui.QLabel("L")
        layout.addWidget(self.LambdaRange, 2, 0) 
        
        # TextField Min
        self.MuTextMin = QtGui.QLineEdit()
        layout.addWidget(self.MuTextMin, 0, 1)  
        self.SigmaTextMin = QtGui.QLineEdit()
        layout.addWidget(self.SigmaTextMin, 1, 1) 
        self.LambdaTextMin = QtGui.QLineEdit()
        layout.addWidget(self.LambdaTextMin, 2, 1)
        
        self.MuTextMin.setText("1")
        self.SigmaTextMin.setText("0")
        self.LambdaTextMin.setText("0")
        
        
        # Button
        self.pushValidation = QtGui.QPushButton("Start")
        layout.addWidget(self.pushValidation, 3, 3)
        
        # Progresss bar
        self.progress = QtGui.QProgressBar(self)
        #self.progress.setGeometry(200, 80, 250, 20)
        layout.addWidget(self.progress, 3, 0, 1, 3)
        
        self.textField = QtGui.QTextEdit()
        layout.addWidget(self.textField, 4, 0, 3, 4)
        
        # add layout
        wid.setLayout(layout)
        
        
        # Connect Button
        self.pushValidation.clicked.connect(self.run_validation)
        
    def run_validation(self):
 
        self.cur_Mu = self.MuTextMin.text()
        self.cur_Sigma = self.SigmaTextMin.text()
        self.cur_Lambda = self.LambdaTextMin.text()
        
        self.x_name = self.x_value
        self.y_name = self.y_value

        self.path2script =  [self.program_path + '/R_model/perc_val.R']
        self.DataFiles = [self.program_path + "/tmp/cur_data.csv"]
        
        self.start_process()

        
    def start_process(self):  
        print("start....")

        self.args = [self.cur_Mu, self.cur_Sigma, self.cur_Lambda]
        self.config = [self.x_name, self.y_name]
        
        command_arg = self.path2script + self.args + self.DataFiles + self.config
        
        #self.results_CV = ""
  
        print(command_arg)
        if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
            try:
                self._process = QtCore.QProcess(self)
                self._process.readyReadStandardOutput.connect(self.processOutput)
                self._process.start(self.command, command_arg, QtCore.QIODevice.ReadOnly)
            except:
                print("process error")

    def processOutput(self):
        self.results_CV = str(self._process.readAllStandardOutput(), encoding = "utf-8")
        #self.textField.setText("For M, S, L: " + self.cur_Mu +", "+ self.cur_Sigma +", "+ self.cur_Lambda + " - compute k-fold CV....\n" + results_CV)
        #self.textField.setText(self.results_CV)
        self.textField.append(self.results_CV)
        
        
