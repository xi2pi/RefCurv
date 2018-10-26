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
from scipy.stats import truncnorm



class Monte_Carlo(QtGui.QMainWindow):    
    def __init__(self, mainWindow):
        super(Monte_Carlo, self).__init__() 
        
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.filename = ""
        self.lms_chart_exists  = False
        self.mw = mainWindow
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
#        self.setWindowTitle('RefCurv 0.3.0 - Monte Carlo Experiment')
        self.setWindowIcon(QIcon( self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.hLayout = QtGui.QHBoxLayout()
        self.mainLayout.insertLayout(1, self.hLayout)
        
        self.setGeometry(50, 50, 500, 500)
        self.center_window()
                
        self.figure_perc = Figure()
        self.canvas = FigureCanvas(self.figure_perc)
        
#        okButton = QtGui.QPushButton("Ok")
#        okButton.clicked.connect(self.calc_zscore)
        
        self.hLayout.addWidget(self.canvas)  
        self.nav = NavigationToolbar(self.canvas, self.canvas, coordinates=False)
        #self.buttonBox = QtGui.QDialogButtonBox(okButton | QtGui.QDialogButtonBox.Cancel)
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.mc)
        
        self.init_createFormGroupBox()
        
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.widget_btns)
        
        # buttons
        loadRefButton = QtGui.QAction("&Load reference curves", self)
        loadRefButton.setStatusTip('Load reference curves')
        loadRefButton.triggered.connect(self.open_loadRefcurves)
        
        loadCurRefButton = QtGui.QAction("&Load current reference curves", self)
        loadCurRefButton.setStatusTip('Load current reference curves')
        loadCurRefButton.triggered.connect(self.open_loadCurRefcurves)
        
        loadSampleButton = QtGui.QAction("&Load sample", self)
        loadSampleButton.setStatusTip('Load sample')
        loadSampleButton.triggered.connect(self.loadSample)
        
        # menu        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Reference curves')
        fileMenu.addAction(loadRefButton)
        fileMenu.addAction(loadCurRefButton)
        SampleMenu = mainMenu.addMenu('&Sample')
        SampleMenu.addAction(loadSampleButton)
 
        
    def init_createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Number of subjects")
        
        self.N_entry = QtGui.QLineEdit()
        
        self.N_entry.setText("5")
        
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel("N value:"), self.N_entry)
        self.formGroupBox.setLayout(layout)
        
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
        
    def y_value(self, L, M, S, z):
        if L == 0:
            y = M*np.exp(S * z)
        else:
            y = M*(1 + L * S * z)**(1/L)
        return y

    def mc(self): 
        if self.lms_chart_exists == True:
            N_sub = int(self.N_entry.text())
            x_MC_values = []
            y_MC_values = []            
            for i in range(0, len(self.lms_chart["x"].values)): 
                M = self.lms_chart["mu"].values[i]
                L = self.lms_chart["nu"].values[i]
                S = self.lms_chart["sigma"].values[i]
            #    print(L,M,S)
                if L > 0:
                    z_values = truncnorm.rvs(-1/(L*S), np.inf, size=N_sub)
                else:
                    z_values = truncnorm.rvs(-np.inf, -1/(L*S), size=N_sub)
                s = np.array([self.y_value(L,M,S, i) for i in z_values])
            
                for j in s:
                    #plt.plot(lms_chart["x"].values[i], j, '.', color = "r")
                    x_MC_values.append(self.lms_chart["x"].values[i])
                    y_MC_values.append(j)
            self.df_sample = pd.DataFrame({'x': x_MC_values, 'y': y_MC_values})
            self.ax_perc.clear()
            self.plot_refcurv()
            self.ax_perc.plot(x_MC_values, y_MC_values, '.', color = "r" )
            self.canvas.draw()
            
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
        if os.path.isfile(self.program_path + "/tmp/percentiles_chart.csv"):
            self.filename = self.program_path + "/tmp/percentiles_chart.csv"
            try:
                self.lms_chart = pd.read_csv(self.program_path + "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()
                self.lms_chart_exists = True

            except:
                print("reading error")
        else:
            print("no charts")
            
    def loadSample(self):
        self.mw.file_flag = True
        self.mw.data = self.df_sample

        self.mw.table_update()
        self.mw.clear_figure()
        self.mw.refcurv_computed = False
        
        self.mw.xCombo.clear()
        self.mw.yCombo.clear()
        
        self.mw.xCombo.addItems(list(self.mw.data.columns.values))
        self.mw.yCombo.addItems(list(self.mw.data.columns.values))
        
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
            
            
        

        


