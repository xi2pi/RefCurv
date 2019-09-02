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
from scipy.optimize import minimize
import scipy.stats as st
import sys
import shutil

from helprefcurv import *


class Reverese_Comp(QtGui.QMainWindow):    
    def __init__(self, mainWindow):
        super(Reverese_Comp, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.filename = ""
        self.lms_chart_exists  = False
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowTitle('RefCurv 0.3.0 - Reverse Computation')
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.vLayout = QtGui.QVBoxLayout()
        self.mainLayout.insertLayout(1, self.vLayout)
        
        self.setGeometry(50, 50, 500, 500)
        self.center_window()
                
        self.figure_perc = Figure()
        self.canvas = FigureCanvas(self.figure_perc)
        
        self.figure_LMS = Figure()
        self.canvas_LMS = FigureCanvas(self.figure_LMS)
        
#        okButton = QtGui.QPushButton("Ok")
#        okButton.clicked.connect(self.calc_zscore)
        
        self.vLayout.addWidget(self.canvas)
        self.vLayout.addWidget(self.canvas_LMS)
        #self.nav = NavigationToolbar(self.canvas, self.canvas, coordinates=False)
        #self.buttonBox = QtGui.QDialogButtonBox(okButton | QtGui.QDialogButtonBox.Cancel)
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.reverse_comp)
        
#        self.init_createFormGroupBox()
        
#        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.widget_btns)
        
        self.popUp = PopUpProcess(self)
        
        # buttons
        loadRefButton = QtGui.QAction("&Load reference curves", self)
        loadRefButton.setStatusTip('Load reference curves')
        loadRefButton.triggered.connect(self.open_loadRefcurves)
        
        loadCurRefButton = QtGui.QAction("&Load current reference curves", self)
        loadCurRefButton.setStatusTip('Load current reference curves')
        loadCurRefButton.triggered.connect(self.open_loadCurRefcurves)
        
        loadResultsButton = QtGui.QAction("&Save results", self)
        loadResultsButton.setStatusTip('Save results')
        loadResultsButton.triggered.connect(self.open_saveResultsDialog)
        
        # menu        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Reference curves')
        fileMenu.addAction(loadRefButton)
        fileMenu.addAction(loadCurRefButton)
        fileMenu.addSeparator()
        fileMenu.addAction(loadResultsButton)
 

        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def z_score(self, L, M, S, y):
#        if L == 0:
#            z = (1/S)*np.log(y/M)
#        else:
        z = (1/(S*L))*(((y/M)**L)-1)
        return z
        
    def y_value(self, L, M, S, z):
        if L == 0:
            y = M*np.exp(S * z)
        else:
            y = M*(1 + L * S * z)**(1/L)
        return y
    
    def p2z(self, value):
        return st.norm.ppf(value)
        
    def error_func(self, para, y):
        L = para[0]
        M = para[1]
        S = para[2]
        
        if L == 0:
            error = np.inf
        else:
                
            
            z_values = self.p2z(np.array([0.03, 0.1, 0.25, 0.5, 0.75, 0.9, 0.97]))
            try:
                y_comp = self.y_value(L, M, S, z_values)
                error = np.sum(np.abs(y - y_comp))
            except:
                error = np.inf
        return error

    def reverse_comp(self):
        if self.lms_chart_exists == True:
            try:
                
                self.popUp.onStart()
                self.popUp.show()
                
                M_array = []
                L_array = []
                S_array = []
                y_0 = np.array([self.lms_chart[i].values[0] for i in ["C3", "C10", "C25", "C50", "C75", "C90", "C97"]])
                para_start = [-0.4, y_0[3], 0.35]
                for j in range(0, len(self.lms_chart["x"].values)):
                    x = self.lms_chart["x"].values[j]
                    y = np.array([self.lms_chart[i].values[j] for i in ["C3", "C10", "C25", "C50", "C75", "C90", "C97"]])
                        
                    res = minimize(self.error_func, para_start, args = (y), method='nelder-mead') 
                    M_array.append(res.x[1])
                    L_array.append(res.x[0])
                    S_array.append(res.x[2])
                    para_start = [res.x[0], res.x[1], res.x[2]]
                
                self.ax_L = self.figure_LMS.add_subplot(311)
                self.ax_M = self.figure_LMS.add_subplot(312)
                self.ax_S = self.figure_LMS.add_subplot(313)
                
                self.ax_L.plot(self.lms_chart["x"].values, L_array, 'b')
                self.ax_M.plot(self.lms_chart["x"].values, M_array, 'b')
                self.ax_S.plot(self.lms_chart["x"].values, S_array, 'b')
                
                self.figure_LMS.tight_layout()
                self.canvas_LMS.draw()
                
                self.popUp.onFinished()
                self.popUp.close()
                
                self.lms_chart["mu"] = pd.DataFrame(M_array)
                self.lms_chart["sigma"] = pd.DataFrame(S_array)
                self.lms_chart["nu"] = pd.DataFrame(L_array)
                
                self.lms_chart.to_csv(self.program_path + "/tmp/results_reverse.csv", sep = ',', encoding = "ISO-8859-1", index = False)
            except:
                print("computation error")
        else:
            print("no charts")
            
        
    def open_loadRefcurves(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()
                self.lms_chart_exists = True

            except:
                print("reading error")

    def open_loadCurRefcurves(self):
        if os.path.isfile(self.program_path +"/tmp/percentiles_chart.csv"):
            self.filename = self.program_path +"/tmp/percentiles_chart.csv"
            try:
                self.lms_chart = pd.read_csv(self.program_path + "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()
                self.lms_chart_exists = True

            except:
                print("reading error")
        else:
            print("no charts")
            
    # Save results dialog
    def open_saveResultsDialog(self):
        if os.path.isfile(self.program_path +"/tmp/results_reverse.csv"):
            try:
                filename_chart = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
                if filename_chart:
                    shutil.copy2(self.program_path +"/tmp/results_reverse.csv", filename_chart)
            except:
                print("copy error")
        else:
            print("no reference curves")

            
    def plot_refcurv(self):
            self.ax_perc = self.figure_perc.add_subplot(111)
            self.ax_perc.clear()
            
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C3"].values, "k")
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C10"].values, "k" )
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C25"].values, "k" )
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C50"].values, "k" )
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C75"].values, "k" )
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C90"].values, "k" )
            self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C97"].values, "k" )
            
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C3"].values[-1], "P3", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C10"].values[-1], "P10", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C25"].values[-1], "P25", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C50"].values[-1], "P50", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C75"].values[-1], "P75", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C90"].values[-1], "P90", size = 8)
            self.ax_perc.text(self.lms_chart["x"].values[-1]*1.01, self.lms_chart["C97"].values[-1], "P97", size = 8)
            
            self.ax_perc.set_xlim([0, self.lms_chart["x"].values[-1]* 1.2])
            self.ax_perc.set_ylim([0, self.lms_chart["C97"].values[-1] * 1.2])
            
            self.ax_perc.grid()
            
            
        

        


