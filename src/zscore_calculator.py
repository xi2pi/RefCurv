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

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None

class Zscore_calculator(QtGui.QMainWindow):    
    def __init__(self, mainWindow):
        super(Zscore_calculator, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.filename = ""
        self.filenamePat = ""
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.setWindowTitle('RefCurv 0.3.0 - Z-score calculator')
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
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
        self.tableWidget = QtGui.QTableView()
        
        self.hLayout.addWidget(self.canvas) 
        self.hLayout.addWidget(self.tableWidget) 
        self.nav = NavigationToolbar(self.canvas, self.canvas, coordinates=False)
        #self.buttonBox = QtGui.QDialogButtonBox(okButton | QtGui.QDialogButtonBox.Cancel)
        self.widget_btns = QtGui.QDialogButtonBox()
        self.widget_btns.addButton('Ok', QtGui.QDialogButtonBox.AcceptRole)
        
        self.widget_btns.accepted.connect(self.calc_zscore)
        
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
        
        loadPatientDataButton = QtGui.QAction("&Load patient data", self)
        loadPatientDataButton.setStatusTip('Load patient data')
        loadPatientDataButton.triggered.connect(self.open_loadPatientData)
        
        PatientCompButton = QtGui.QAction("&Compute z-scores", self)
        PatientCompButton.setStatusTip('&Compute z-scores')
        PatientCompButton.triggered.connect(self.open_loadPatientComp)
        
        PatientSaveButton = QtGui.QAction("&Save z-scores", self)
        PatientSaveButton.setStatusTip('&Save z-scores')
        PatientSaveButton.triggered.connect(self.open_saveZscores)
        
        # menu        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Reference curves')
        fileMenu.addAction(loadRefButton)
        fileMenu.addAction(loadCurRefButton)
        
        fileMenuPat = mainMenu.addMenu('&Patient data')
        fileMenuPat.addAction(loadPatientDataButton)
        fileMenuPat.addAction(PatientCompButton)
        fileMenuPat.addAction(PatientSaveButton)

  
 
 
        
    def init_createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Z-score values")
        
        self.x_entry = QtGui.QLineEdit()
        self.y_entry = QtGui.QLineEdit()
        
        self.x_entry.setText("50")
        self.y_entry.setText("50")
        
        
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel("x value:"), self.x_entry)
        layout.addRow(QtGui.QLabel("y value:"), self.y_entry)
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
        
    def calc_zscore(self):
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename ,sep =',', encoding = "ISO-8859-1")
                x = self.lms_chart["x"].values
                y = float(self.x_entry.text())
                M_array = self.lms_chart["mu"].values
                S_array = self.lms_chart["sigma"].values
                L_array = self.lms_chart["nu"].values
                
                self.f_M = interpolate.interp1d(x, M_array,  kind = "linear")
                self.f_S = interpolate.interp1d(x, S_array,  kind = "linear")
                self.f_L = interpolate.interp1d(x, L_array,  kind = "linear")
                
                #idx = (np.abs(x - float(self.x_entry.text()))).argmin()
                #print(idx)
                #z = self.z_score(L_array[idx], M_array[idx], S_array[idx], float(self.y_entry.text()))
                #print(z)
                z = self.z_score(self.f_L(y), self.f_M(y), self.f_S(y), float(self.y_entry.text()))
                    
                self.plot_refcurv()
                self.ax_perc.annotate(
                    "Z-score\n"+ str(round(z, 4)),
                    xy=(float(self.x_entry.text()), float(self.y_entry.text())), xytext=(-15, 15),
                    textcoords='offset points', ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=1),
                    arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))
                self.ax_perc.plot(float(self.x_entry.text()), float(self.y_entry.text()),  color="r", marker="o", markersize = 5) 
                self.canvas.draw()
            except Exception as e: print(e)
        else:
            print("not data loaded")
        
        
    def open_loadRefcurves(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()

            except:
                print("reading error")

    def open_loadCurRefcurves(self):
        if os.path.isfile(self.program_path+"/tmp/percentiles_chart.csv"):
            self.filename = self.program_path+"/tmp/percentiles_chart.csv"
            try:
                self.lms_chart = pd.read_csv(self.program_path + "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
                self.plot_refcurv()
                self.canvas.draw()

            except:
                print("reading error")
        else:
            print("no charts")
            
    def open_loadPatientData(self):
        self.filenamePat = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filenamePat:
            try:
                self.df = pd.read_csv(self.filenamePat,sep =',', encoding = "ISO-8859-1")
                model = PandasModel(self.df)
                self.tableWidget.setModel(model)
                
                self.plot_refcurv()
                self.ax_perc.plot(self.df["x"].values, self.df["y"].values,  color="r", marker="o", linestyle='None', markersize = 5) 
                self.canvas.draw()
            except:
                print("reading error")
                
    def open_loadPatientComp(self):
        if self.filenamePat and self.filename:
            try:
                x = self.lms_chart["x"].values
                y = float(self.x_entry.text())
                M_array = self.lms_chart["mu"].values
                S_array = self.lms_chart["sigma"].values
                L_array = self.lms_chart["nu"].values
                
                self.f_M = interpolate.interp1d(x, M_array,  kind = "linear")
                self.f_S = interpolate.interp1d(x, S_array,  kind = "linear")
                self.f_L = interpolate.interp1d(x, L_array,  kind = "linear")
                z_scores = [self.z_score(self.f_L(self.df["x"].values[i]), self.f_M(self.df["x"].values[i]), self.f_S(self.df["x"].values[i]), self.df["y"].values[i]) for i in range(0, len(self.df["x"].values))]
    #            print(z_scores)
                self.df["z-score"] =  pd.DataFrame(z_scores)           
    #            
                model = PandasModel(self.df)
                self.tableWidget.setModel(model)
    
            except Exception as e: print(e)
        else:
            print("no data")
    
    def open_saveZscores(self):
        try:
            filename_chart = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
            if filename_chart:
                self.df.to_csv(filename_chart, sep = ',', encoding = "ISO-8859-1", index = False)
        except:
            print("copy error")


            
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
            
            
        

        


