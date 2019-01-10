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

from scipy import interpolate
from scipy.special import gamma, erf


class Model_Comparison(QtGui.QMainWindow):    
    def __init__(self, mainWindow):
        super(Model_Comparison, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.filename = ""
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowTitle('RefCurv 0.3.0 - Model comparison')
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
        
        self.figure_result = Figure()
        self.canvas_result = FigureCanvas(self.figure_result)
        
        self.qbox = QtGui.QComboBox()
        self.qbox.addItems(["C3", "C10", "C25", "C50", "C75", "C90", "C97", "Area"])

        self.vLayout.addWidget(self.canvas) 
        self.vLayout.addWidget(self.qbox)
        self.vLayout.addWidget(self.canvas_result)
        #self.nav = NavigationToolbar(self.canvas, self.canvas, coordinates=False)
        #self.buttonBox = QtGui.QDialogButtonBox(okButton | QtGui.QDialogButtonBox.Cancel)
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        self.widget_btns.accepted.connect(self.compare_model)
        self.mainLayout.addWidget(self.widget_btns)
        
        # buttons
        loadRefButton = QtGui.QAction("&Load reference curve", self)
        loadRefButton.setStatusTip('Load reference curve')
        loadRefButton.triggered.connect(self.open_loadRefcurves)
        
        loadCurRefButton = QtGui.QAction("&Load current reference curve", self)
        loadCurRefButton.setStatusTip('Load current reference curve')
        loadCurRefButton.triggered.connect(self.open_loadCurRefcurves)
        
        loadRefButton2 = QtGui.QAction("&Load reference curve", self)
        loadRefButton2.setStatusTip('Load reference curve')
        loadRefButton2.triggered.connect(self.open_loadRefcurves2)
        
        loadCurRefButton2 = QtGui.QAction("&Load current reference curve", self)
        loadCurRefButton2.setStatusTip('Load current reference curve')
        loadCurRefButton2.triggered.connect(self.open_loadCurRefcurves2)
        
        # menu        
        mainMenu = self.menuBar()
        fileMenu1 = mainMenu.addMenu('&Reference curve 1')
        fileMenu1.addAction(loadRefButton)
        fileMenu1.addAction(loadCurRefButton)
        fileMenu2 = mainMenu.addMenu('&Reference curve 2')
        fileMenu2.addAction(loadRefButton2)
        fileMenu2.addAction(loadCurRefButton2)
        
    def BCCG(self,params,x):
        L = params[0]
        M = params[1]
        S = params[2]
        
        Phi = 0.5*(1 + erf((1/(S*np.abs(L)))/(np.sqrt(2))))
        
        if L == 0:
            z = (1/S)*np.log(x/M)
        else:
            z = (1/(S*L))*(((x/M)**L)-1)
        
        f = (x**(L-1)*np.exp(-0.5*z**2))/((M**L)*S*Phi*np.sqrt(2*np.pi))
        return f
     
    def compare_model(self):
        self.ax_result = self.figure_result.add_subplot(111)
        self.ax_result.clear()
        print(self.qbox.currentText())
    
        if self.qbox.currentText() == "Area":
            print(self.area_intersection())
            self.ax_result.plot(self.lms_chart["x"].values, self.area_intersection(), "k")
        else:
            cur_perc_diff = self.lms_chart[self.qbox.currentText()].values - self.lms_chart2[self.qbox.currentText()].values
        
            self.ax_result.plot(self.lms_chart["x"].values, cur_perc_diff, "k")
        
        self.canvas_result.draw()
        
        
    def area_intersection(self):
        area = []
        for i in range(0, len(self.lms_chart["x"].values)):
            L1 = self.lms_chart["nu"].values[i]
            M1 = self.lms_chart["mu"].values[i]
            S1 = self.lms_chart["sigma"].values[i]
            
            L2 = self.lms_chart2["nu"].values[i]
            M2 = self.lms_chart2["mu"].values[i]
            S2 = self.lms_chart2["sigma"].values[i]
            
            y_middle = np.mean([self.lms_chart["mu"].values[i], self.lms_chart2["mu"].values[i]])
            y_range = np.linspace(0, 5*y_middle, 1000)
            #print(y_middle)
            #print(L1,L2,M1,M2,S1,S2)
            #print(self.BCCG([L1, M1, S1], y_range))
            
           
            area.append(self.dist_intersection(self.BCCG([L1, M1, S1], y_range), self.BCCG([L2, M2, S2], y_range), y_range))
        #self.ax_result.plot(y_range, self.BCCG([L1, M1, S1], y_range))      
        return area
                        
        
    def dist_intersection(self, d1, d2, bins):
       bins = np.diff(bins)
       sm = 0
       for i in range(len(bins)):
           sm += min(bins[i]*d1[i], bins[i]*d2[i])
       return sm
        
        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def z_score(self, L, M, S, y):
        if L == 0:
            z = (1/S)*np.log(y/M)
        else:
            z = (1/(S*L))*(((y/M)**L)-1)
        return z
        
        
    def open_loadRefcurves(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv(121)
                self.canvas.draw()

            except:
                print("reading error")

    def open_loadCurRefcurves(self):
        if os.path.isfile(self.program_path +"/tmp/percentiles_chart.csv"):
            self.filename = self.program_path +"/tmp/percentiles_chart.csv"
            try:
                self.lms_chart = pd.read_csv(self.program_path + "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv(121)
                self.canvas.draw()

            except:
                print("reading error")
        else:
            print("no charts")
            
    def open_loadRefcurves2(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv(122)
                self.canvas.draw()

            except:
                print("reading error")

    def open_loadCurRefcurves2(self):
        if os.path.isfile(self.program_path +"/tmp/percentiles_chart.csv"):
            self.filename = self.program_path +"/tmp/percentiles_chart.csv"
            try:
                self.lms_chart2 = pd.read_csv(self.program_path+ "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv2(122)
                self.canvas.draw()

            except:
                print("reading error")
        else:
            print("no charts")
            
            
    def plot_refcurv(self, plt_number):
        self.ax_perc = self.figure_perc.add_subplot(plt_number)
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
        
    def plot_refcurv2(self, plt_number):
        self.ax_perc = self.figure_perc.add_subplot(plt_number)
        self.ax_perc.clear()
        
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C3"].values, "k")
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C10"].values, "k" )
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C25"].values, "k" )
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C50"].values, "k" )
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C75"].values, "k" )
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C90"].values, "k" )
        self.ax_perc.plot(self.lms_chart2["x"].values, self.lms_chart2["C97"].values, "k" )
        
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C3"].values[-1], "P3", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C10"].values[-1], "P10", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C25"].values[-1], "P25", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C50"].values[-1], "P50", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C75"].values[-1], "P75", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C90"].values[-1], "P90", size = 8)
        self.ax_perc.text(self.lms_chart2["x"].values[-1]*1.01, self.lms_chart2["C97"].values[-1], "P97", size = 8)
        
        self.ax_perc.set_xlim([0, self.lms_chart2["x"].values[-1]* 1.2])
        self.ax_perc.set_ylim([0, self.lms_chart2["C97"].values[-1] * 1.2])
        
        self.ax_perc.grid()


        

        


