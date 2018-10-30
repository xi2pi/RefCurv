 # -*- coding: utf-8 -*-

# Author: Christian Winkler
# Date: 12-06-2018

import numpy as np
import pandas as pd
#from shutil import copyfile
 
#from guidata.qt.QtGui import QMainWindow, QSplitter
#
#from guidata.dataset.datatypes import DataSet
#from guidata.dataset.dataitems import FileOpenItem
#from guidata.configtools import get_icon
#from guidata.qthelpers import create_action, add_actions, get_std_icon

from PyQt4 import QtCore, QtGui
#from PyQt4.QtCore import QProcess
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import sys
import os
#import pyqtgraph as PG
#from PyQt4 import QtGui
#from PyQt4 import QtCore
#from PyQt4.QtGui import * 
#from PyQt4.QtCore import *
#import scipy.optimize as optimization

#import plugin.pv_loop.ode_solver as ode_solver
#from guidata.configtools import get_icon

 
#-----------------------------------
#class SmoothGUI(DataSet):
#
#    fname = FileOpenItem("Open file", ("txt", "csv"), "")
#    
  
#-----------------------------------
class pvloop_window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        #QMainWindow.__init__(self)
        super(pvloop_window, self).__init__() 
        #self.setWindowIcon(get_icon('python.png'))
        self.setWindowTitle("PV Loop Simulation")
        self.setWindowTitle('RefCurv 0.3.0 - PV Loop Simulation')
        #self.setWindowIcon(get_icon(os.getcwd() +'/logo/refcurv_logo.png'))
        
        pal=QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
       
        #self.textEdit = QtGui.QLabel('None')

        self.loadButton = QtGui.QPushButton("Load")
        self.loadButton.clicked.connect(self.on_click)
        self.loadPercButton = QtGui.QPushButton("Load Reference curves")
        self.loadPercButton.clicked.connect(self.loadRef)
        self.applyDataButton = QtGui.QPushButton("ApplyData")
        self.applyDataButton.clicked.connect(self.applyData)
        self.clearButton = QtGui.QPushButton('Clear Plot', self)
        self.clearButton.clicked.connect(self.clearPlots)
         #self.connect(self.smoothGB, SIGNAL("apply_button_clicked()"),
         #self.update_window)
        
        self.dropDownMenu = QtGui.QComboBox()
        self.dropDownMenu.addItems(["Pmax", "Pmin", "Vmax", "Vmin"])
        self.table1 = QtGui.QTableWidget()
        self.table2 = QtGui.QTableWidget()
         
        self.fileName = ''
        self.lastClicked = []
        self.number_plots = 0     
        self.chosen_point = 0

        
        self.figure1 = Figure()
        self.pw1 = FigureCanvas(self.figure1)

        self.figure2 = Figure()
        self.pw2 = FigureCanvas(self.figure2)
        
        self.figure3 = Figure()
        self.pw3 = FigureCanvas(self.figure3)
        
        self.figure_perc = Figure()
        self.pw_perc = FigureCanvas(self.figure_perc)
        
        #horizontalLayout = QtGui.QHBoxLayout(self)
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitterH = QtGui.QSplitter(QtCore.Qt.Horizontal)
        

        splitter.addWidget(self.loadButton)
        splitter.addWidget(self.pw1)
        splitter.addWidget(self.pw2)
        splitter.addWidget(self.pw3)
        splitter.addWidget(self.clearButton)
        
        splitter2.addWidget(self.table1)
#        splitter2.addWidget(self.table2)
        splitter2.addWidget(self.loadPercButton)
        splitter2.addWidget(self.pw_perc)
        splitter2.addWidget(self.dropDownMenu)
        splitter2.addWidget(self.applyDataButton)
    
        
        splitterH.addWidget(splitter)
        splitterH.addWidget(splitter2)
        
        self.table1.setRowCount(6)
        self.table1.setColumnCount(2)
        
#        self.table2.setRowCount(8)
#        self.table2.setColumnCount(2)
        

        self.table1.setItem(0,0, QtGui.QTableWidgetItem("HR [bpm]"))
        self.table1.setItem(0,1, QtGui.QTableWidgetItem("70"))
        self.table1.setItem(1,0, QtGui.QTableWidgetItem("Pmax [mmHg]"))
        self.table1.setItem(1,1, QtGui.QTableWidgetItem("100"))
        self.table1.setItem(2,0, QtGui.QTableWidgetItem("Pmin [mmHg]"))
        self.table1.setItem(2,1, QtGui.QTableWidgetItem("6"))
        self.table1.setItem(3,0, QtGui.QTableWidgetItem("Vmax [ml]"))
        self.table1.setItem(3,1, QtGui.QTableWidgetItem("100"))
        self.table1.setItem(4,0, QtGui.QTableWidgetItem("Vmin [ml]"))
        self.table1.setItem(4,1, QtGui.QTableWidgetItem("70"))
        self.table1.setItem(5,0, QtGui.QTableWidgetItem("Vd [ml]"))
        self.table1.setItem(5,1, QtGui.QTableWidgetItem("0"))
        self.table1.setItem(6,0, QtGui.QTableWidgetItem("-"))
        self.table1.setItem(6,1, QtGui.QTableWidgetItem("-"))
        self.table1.setItem(7,0, QtGui.QTableWidgetItem("-"))
        self.table1.setItem(7,1, QtGui.QTableWidgetItem("-"))
        self.table1.setItem(8,0, QtGui.QTableWidgetItem("-"))
        self.table1.setItem(8,1, QtGui.QTableWidgetItem("-"))
              
        self.setCentralWidget(splitterH)
 
        self.setContentsMargins(10, 5, 10, 5)
        self.setGeometry(100, 100, 1000, 800)
        self.center_window()
        
         # File menu
#        file_menu = self.menuBar().addMenu("File")
#        quit_action = create_action(self, "Quit",
#        shortcut="Ctrl+Q",
#        icon=get_std_icon("DialogCloseButton"),
#        tip="Quit application",
#        triggered=self.close)
#        add_actions(file_menu, (quit_action, ))
        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        
    def clearPlots(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        self.pw1.draw()
        self.pw2.draw()
        self.pw3.draw()
         
         
    def on_click(self):
        
        HR = float(self.table1.item(0,1).text())
        Pmax = float(self.table1.item(1,1).text())
        Pmin = float(self.table1.item(2,1).text())
        Vmax = float(self.table1.item(3,1).text())
        Vmin = float(self.table1.item(4,1).text())
        Vd = float(self.table1.item(5,1).text())
        
        vtc = pd.read_csv("./plugin/pv_loop/vtc.csv",sep =',', encoding = "ISO-8859-1",index_col=False)
        ptc = pd.read_csv("./plugin/pv_loop/ptc.csv",sep =',', encoding = "ISO-8859-1",index_col=False)
        
        T = vtc["x0000"].values[2999:]
        t = (T-min(T))/(max(T)-min(T))
        V = vtc["y0000"].values[2999:]
        v = (V - min(V))/(max(V)-min(V)) 
        
        P = ptc["y0000"].values[2999:]
        p = (P - min(P))/(max(P)-min(P)) 
        

        HC = 1/HR*60        
        t_comp = t * HC
        V_comp = (Vmax - Vmin)* v + Vmin
        P_comp = (Pmax - Pmin)* p + Pmin
        
        # elastance
        Emax = self.find_emax(V_comp, P_comp, Vd)
        Emin = self.find_emin(V_comp, P_comp, Vd)
        
        W = self.compute_work(Emax, Emin, V_comp, P_comp)
        
#        print(Emin[1])
#        print(Emax[1])
        print(W)
              
        self.ax1 = self.figure1.add_subplot(111)
        self.ax1.plot(t_comp, V_comp)
        self.ax2 = self.figure2.add_subplot(111)
        self.ax2.plot(t_comp, P_comp)
        
        # PV Loop
        self.ax3 = self.figure3.add_subplot(111)
        self.ax3.plot(V_comp, P_comp, label = "cardiac work = " + str(round(W, 3)))
        self.ax3.plot(np.linspace(0,Vmax,100), Emax[0]*(np.linspace(0,Vmax,100)-Vd))
        self.ax3.plot(np.linspace(0,Vmax,100), Emin[0]*(np.linspace(0,Vmax,100)-Vd))
        self.ax3.legend()
    
        self.pw1.draw()
        self.pw2.draw()
        self.pw3.draw()

        
        self.figure_perc.canvas.mpl_connect('button_press_event', self.pw_perc_click)
             
        
        print('PV loop computed')
        
    def find_emax(self, V, P, Vd):
        E = P/(V-Vd)
        #print("E length" + str(len(E)))
        ind_emax = np.argmax(E)
        return [max(E), ind_emax]
        
    def find_emin(self, V, P, Vd):
        E = P/(V-Vd)
        ind_emin = np.argmin(E)
        return [min(E), ind_emin]
        
    def compute_work(self, Emax, Emin, V, P):
        P_con = P * 133.322
        V_con = V * (10**-6)
        dV = V_con - np.roll(V_con, -1)
        print("Emin ind" + str(Emin[1] ))
        print("Emax ind" + str(Emax[1] ))
        if Emin[1] < 50:
            W_in = np.sum(np.multiply(P_con[Emin[1]:Emax[1]],  dV[Emin[1]:Emax[1]]))
            W_out = np.sum(np.multiply(P_con[Emax[1]:],  dV[Emax[1]:]))
        else:
            W_in = np.sum(np.multiply(P_con[:Emax[1]],  dV[:Emax[1]]))
            W_out = np.sum(np.multiply(P_con[Emax[1]:Emin[1]],  dV[Emax[1]:Emin[1]]))
            
        W_in = np.sum(np.multiply(P_con[:Emax[1]],  dV[:Emax[1]]))
        print("W in" + str(W_in))
        print("W out" + str(W_out))
        return(W_in-W_out)
    
    def pw_perc_click(self, event):
        self.ax_perc.clear()
        self.pw_perc.draw()
        
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
        #self.ax_perc.set_xlim([0, 100])
        #self.ax_perc.set_ylim([0, 50])
        self.ax_perc.plot(event.xdata, event.ydata,  color="r", marker="o", markersize = 5) 
        
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C3"].values, "k")
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C10"].values, "k" )
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C25"].values, "k" )
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C50"].values, "k" )
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C75"].values, "k" )
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C90"].values, "k" )
        self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C97"].values, "k" )
        
        self.ax_perc.set_xlim([0, self.lms_chart["x"].values[-1]* 1.2])
        self.ax_perc.set_ylim([0, self.lms_chart["C97"].values[-1] * 1.2]) 

        self.ax_perc.grid()
           
        self.pw_perc.draw()
        self.chosen_point = round(event.ydata, 2)
    
    def loadRef(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.lms_chart = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                
                self.ax_perc = self.figure_perc.add_subplot(111)
                self.ax_perc.clear()
                
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C3"].values, "k")
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C10"].values, "k" )
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C25"].values, "k" )
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C50"].values, "k" )
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C75"].values, "k" )
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C90"].values, "k" )
                self.ax_perc.plot(self.lms_chart["x"].values, self.lms_chart["C97"].values, "k" )
                
                self.ax_perc.set_xlim([0, self.lms_chart["x"].values[-1]* 1.2])
                self.ax_perc.set_ylim([0, self.lms_chart["C97"].values[-1] * 1.2])
                
                self.ax_perc.grid()
                
                self.pw_perc.draw()

            except:
                print("reading error")

            print(self.filename)      
    
    def applyData(self):
        if self.dropDownMenu.currentText() == "Pmax":
            self.table1.setItem(1,1, QtGui.QTableWidgetItem(str(self.chosen_point)))
        elif self.dropDownMenu.currentText() == "Pmin":
            self.table1.setItem(2,1, QtGui.QTableWidgetItem(str(self.chosen_point)))
        elif self.dropDownMenu.currentText() == "Vmax":
            self.table1.setItem(3,1, QtGui.QTableWidgetItem(str(self.chosen_point)))
        elif self.dropDownMenu.currentText() == "Vmin":
            self.table1.setItem(4,1, QtGui.QTableWidgetItem(str(self.chosen_point)))
        else:
            print("error")

        

        