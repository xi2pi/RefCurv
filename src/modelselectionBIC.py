# -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import subprocess
import os
from functools import partial
import numpy as np
import pandas as pd
import sys

from helprefcurv import *


class ModelSelectionBIC(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ModelSelectionBIC, self).__init__()
        self.program_path = os.path.dirname(sys.argv[0])

        #self.setWindowTitle('RefCurv 0.3.0 - Model Selection BIC')
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)       
        
        self.x_value = None
        self.y_value = None
        
        self.fileName = None
        
        self.command = 'Rscript'
        
        self.setGeometry(50, 50, 500, 300)
        self.center()
        self.setupUI()

    def setupUI(self):
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        layout = QtGui.QGridLayout()
       
        # Labels
        self.MuRange = QtGui.QLabel("M_df range:")
        layout.addWidget(self.MuRange, 0, 0)  
        self.SigmaRange = QtGui.QLabel("S_df range:")
        layout.addWidget(self.SigmaRange, 1, 0) 
        self.LambdaRange = QtGui.QLabel("L_df range:")
        layout.addWidget(self.LambdaRange, 2, 0) 
        
        # TextField Min
        self.MuTextMin = QtGui.QLineEdit()
        layout.addWidget(self.MuTextMin, 0, 1)  
        self.SigmaTextMin = QtGui.QLineEdit()
        layout.addWidget(self.SigmaTextMin, 1, 1) 
        self.LambdaTextMin = QtGui.QLineEdit()
        layout.addWidget(self.LambdaTextMin, 2, 1)
        
        self.MuTextMin.setText("0")
        self.SigmaTextMin.setText("0")
        self.LambdaTextMin.setText("0")
        
        # TextField Max
        self.MuTextMax = QtGui.QLineEdit()
        layout.addWidget(self.MuTextMax, 0, 2)  
        self.SigmaTextMax = QtGui.QLineEdit()
        layout.addWidget(self.SigmaTextMax, 1, 2) 
        self.LambdaTextMax = QtGui.QLineEdit()
        layout.addWidget(self.LambdaTextMax, 2, 2)
        
        self.MuTextMax.setText("1")
        self.SigmaTextMax.setText("1")
        self.LambdaTextMax.setText("1")
        
        # Button
        self.pushOptimization = QtGui.QPushButton("Start")
        layout.addWidget(self.pushOptimization, 3, 3)
        
        
        # Table
        self.table = QtGui.QTableWidget()
        #self.table.setColumnCount(8)
        layout.addWidget(self.table, 4, 0, 3, 4)
        
        # add layout
        wid.setLayout(layout)
        
        # Connect Button
        self.pushOptimization.clicked.connect(self.run_optimization)
#        self.resultButton.clicked.connect(self.show_result)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
        
    def run_optimization(self):
        print(self.command)
                
        self.table.clear()
        self.table.setSortingEnabled(False)
        

        self.M_Min = int(self.MuTextMin.text())
        self.S_Min = int(self.SigmaTextMin.text())
        self.L_Min = int(self.LambdaTextMin.text()) 
        
        self.M_Max = int(self.MuTextMax.text()) + 1
        self.S_Max = int(self.SigmaTextMax.text()) + 1
        self.L_Max = int(self.LambdaTextMax.text()) + 1
        
        manager = TaskManager()
        manager.command = self.command
        manager.x_axis = self.x_value
        manager.y_axis = self.y_value
        manager.start_process(self.M_Min,self.M_Max, self.S_Min,self.S_Max, self.L_Min,self.L_Max)
        manager.resultsChanged.connect(self.on_finished)
        

    def on_finished(self, results):
        print("results:")
        print(pd.DataFrame(results))
        
        self.table.setRowCount((self.M_Max - self.M_Min) * (self.S_Max - self.S_Min) * (self.L_Max - self.L_Min))
        self.table.setColumnCount(4)

        for n, key in enumerate(sorted(results.keys())):
            #horHeaders.append(key)
            for m, item in enumerate(results[key]):
                newitem = QtGui.QTableWidgetItem(item)
                self.table.setItem(m, n, newitem)
        
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.AscendingOrder,    )
        
        self.table.setHorizontalHeaderLabels(["BIC", "Mu", "Sigma", "Lambda"])

class TaskManager(QtCore.QObject):
    resultsChanged = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        
        self.program_path = os.path.dirname(sys.argv[0])
        self.command = self.program_path + '/Rscript'
        
        self.BIC = []
        self.M = []
        self.S = []
        self.L = []
        self.m_processes = []
        self.number_process_running = 0
        self.process_id = 0
        self.x_axis = "x"
        self.y_axis = "y"
        
        self.dimension = 0
        self.completed = 0 
        self.popUp = PopUpProcess(self)
        self.popUp.pbar.setRange(0, 100)
    

    def start_process(self, m_min, m_max, s_min, s_max, l_min, l_max):
        print("start....")
        self.popUp.show()
        
        config = [self.x_axis, self.y_axis]
        
        path2script =  [self.program_path + '/R_model/perc_opt.R']
        fileName = [self.program_path + "/tmp/cur_data.csv"]
#        path2script =  ['R_model/perc_opt.R']
#        fileName = ["/tmp/cur_data.csv"]
        print(path2script)
        print(fileName)
        self.command_arg_list = []
        
        self.dimension = (m_max - m_min) * (s_max - s_min) * (l_max - l_min)
        

        for i in range(int(m_min), int(m_max)):
            for j in range(int(s_min), int(s_max)):
                for k in range(int(l_min), int(l_max)):
                    args = [str(int(i)), str(int(j)), str(int(k))]
                    command_arg = path2script + args + fileName + config
                    self.command_arg_list.append(command_arg)
                    
        
        if self.dimension < 16:
            self.run_parallel(self.command, self.command_arg_list)
            
        else:
            print("too many points")
            self.run_queue(self.command, self.command_arg_list)

            
    def split(self, arr, size):
         arrs = []
         while len(arr) > size:
             pice = arr[:size]
             arrs.append(pice)
             arr   = arr[size:]
         arrs.append(arr)
         return arrs
            
    def run_queue_2(self, command, command_arg_list):
                    
        length_queue = len(command_arg_list)
        self.process_id_2 = 0
        print(length_queue)

        if self.process_id_2 < length_queue:
            cur_process = command_arg_list[self.process_id_2]

            print(self.process_id_2)
            process = QtCore.QProcess(self)
            process.readyReadStandardOutput.connect(partial(self.onReadyReadStandardOutput_queue_2, self.process_id_2, cur_process))
            process.start(command,cur_process, QtCore.QIODevice.ReadOnly)

            
        else:
            print("wait")
            
    def run_queue(self, command, command_arg_list):
        print(command)
        self.length_queue = len(command_arg_list)
        print(self.length_queue)
        
        if self.process_id < self.length_queue:
            cur_process = command_arg_list[self.process_id]

            print(self.process_id)
            process = QtCore.QProcess(self)
            process.readyReadStandardOutput.connect(partial(self.onReadyReadStandardOutput_queue, self.process_id, cur_process))
            process.start(command, cur_process, QtCore.QIODevice.ReadOnly)
            self.m_processes.append(process)
            
        else:
            print("wait") 
    
    def run_parallel(self, command, command_arg_list):
                    
        for i, cmd_arg in enumerate(command_arg_list):
            print(i)
            print(cmd_arg)
            process = QtCore.QProcess(self)
            process.readyReadStandardOutput.connect(partial(self.onReadyReadStandardOutput, i, cmd_arg))
            process.start(command, cmd_arg, QtCore.QIODevice.ReadOnly)
            self.m_processes.append(process)
            self.number_process_running += 1
            self.completed += 1.0/(self.dimension)*100/2
            self.popUp.pbar.setValue(self.completed)
            

    def onReadyReadStandardOutput(self, i, cmd_arg):
        print("finished. getting results:")
        process = self.sender()
        try:
            resBIC = str(process.readAllStandardOutput(), encoding = "utf-8").split(" ")[1]
            if resBIC == '"-"\r\n':
                self.BIC.append("")
            else:
                self.BIC.append(resBIC)
            print(resBIC)
        except:
            self.BIC.append("-")
        self.M.append(cmd_arg[1])
        self.S.append(cmd_arg[2])
        self.L.append(cmd_arg[3])
                
        self.number_process_running -= 1
        self.completed += 1.0/(self.dimension)*100/2
        #print(self.completed)
        self.popUp.pbar.setValue(self.completed)
        if self.number_process_running <= 0:
            data = {2: self.M,
                    3: self.S,
                    4: self.L,
                    1: self.BIC}
            self.resultsChanged.emit(data)
            self.popUp.close()
            self.selectionFinishedWindow()
    
    def onReadyReadStandardOutput_queue(self, i, cmd_arg):
        print("finished. getting results:")
        process = self.sender()
        try:
            resBIC = str(process.readAllStandardOutput(), encoding = "utf-8").split(" ")[1]
            if resBIC == '"-"\r\n':
                self.BIC.append("")
            else:
                self.BIC.append(resBIC)
            print(resBIC)
        except:
            self.BIC.append("-")
        self.M.append(cmd_arg[1])
        self.S.append(cmd_arg[2])
        self.L.append(cmd_arg[3])
                
        self.process_id += 1
        self.run_queue(self.command, self.command_arg_list)
                
        self.completed += 1.0/(self.dimension)*100

        self.popUp.pbar.setValue(self.completed)
        if self.process_id >= self.length_queue:
            data = {2: self.M,
                    3: self.S,
                    4: self.L,
                    1: self.BIC}
            self.resultsChanged.emit(data)
            self.popUp.close()
            self.selectionFinishedWindow()
            
    def onReadyReadStandardOutput_queue_2(self, i, cmd_arg):
        print("finished. getting results:")
        process = self.sender()
        try:
            resBIC = str(process.readAllStandardOutput(), encoding = "utf-8").split(" ")[1]
            if resBIC == '"-"\r\n':
                self.BIC.append("")
            else:
                self.BIC.append(resBIC)
            print(resBIC)
        except:
            self.BIC.append("-")
        self.M.append(cmd_arg[1])
        self.S.append(cmd_arg[2])
        self.L.append(cmd_arg[3])
                
        self.process_id_2 += 1
        self.run_queue(self.command, self.command_arg_list)
                
        if i >= self.length_queue:
            data = {2: self.M,
                    3: self.S,
                    4: self.L,
                    1: self.BIC}
            self.resultsChanged.emit(data)
    
    def selectionFinishedWindow(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        msgBox.setText("The model selection was successful!")
        msgBox.setWindowTitle("Model Selection")
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        retval = msgBox.exec_()
