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
import shutil
import subprocess
import sys

from functools import partial

from treeitems import *
from helprefcurv import *

class SensitvityAnalysis(QtGui.QMainWindow):    
    def __init__(self, parent=None):
        super(SensitvityAnalysis, self).__init__() 
        self.program_path = os.path.dirname(sys.argv[0])               
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        #self.setWindowTitle('RefCurv 0.3.0 - Sensitivity Analysis')
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)

        self.hLayout = QtGui.QHBoxLayout()
        self.mainLayout.insertLayout(1, self.hLayout)
        
        self.setGeometry(50, 50, 1000, 800)
        self.center_window()
        
        self.m_processes = []
        self.number_process_running = 0
        self.process_id = 0
        
        self.data = 0
        
        self.x_value = "x"
        self.y_value = "y"
        
        self.command = 'Rscript'
        
        
        self.treeWidget=QtGui.QTreeWidget()
        self.treeWidget.itemClicked.connect(self.handler)
        
        self.hLayout.addWidget(self.treeWidget)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.hLayout.addWidget(self.canvas)
        
        self.nav = NavigationToolbar(self.canvas, self.canvas, coordinates=False)
      
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.plottingButton)
        self.buttonBox.rejected.connect(self.reject)
        
        self.init_createFormGroupBox()
        
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.buttonBox)
 
        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def init_createFormGroupBox(self):
        self.formGroupBox = QtGui.QGroupBox("Sensitivity Analysis - Configuration")
        
        self.Mu = QtGui.QLineEdit()
        self.Sigma = QtGui.QLineEdit()
        self.Lambda = QtGui.QLineEdit()
        
        self.Mu.setText("1")
        self.Sigma.setText("0")
        self.Lambda.setText("0")
        
        self.Variation_up = QtGui.QLineEdit()
        self.Variation_down  = QtGui.QLineEdit() 
        
        self.Variation_up.setText("1.0")
        self.Variation_down.setText("1.0")
        
        layout = QtGui.QFormLayout()
        layout.addRow(QtGui.QLabel("e.d.f. Mu:"), self.Mu)
        layout.addRow(QtGui.QLabel("e.d.f. Sigma"), self.Sigma)
        layout.addRow(QtGui.QLabel("e.d.f. Lambda"), self.Lambda)
        layout.addRow(QtGui.QLabel(" "))
        layout.addRow(QtGui.QLabel("Variation up"), self.Variation_up)
        layout.addRow(QtGui.QLabel("Variation down"), self.Variation_down)
        self.formGroupBox.setLayout(layout)
        
    def init_table(self):
        self.HEADERS = ["checkbox"] + list(self.data)
        self.treeWidget.setColumnCount( len(self.HEADERS) )
        self.treeWidget.setHeaderLabels( self.HEADERS )
 
 
        dataList = self.data.values.tolist()
        for i in range(0, len(dataList)):
            item = CustomTreeItem_unchecked(self.treeWidget, dataList[i])
 
        ## Set Columns Width to match content:
        for column in range( self.treeWidget.columnCount() ):
            self.treeWidget.resizeColumnToContents(column)
        
    
    def init_plot(self):
        self.ax = self.figure.add_subplot(111)
        
        self.ax.clear()
        
        self.ax.set_xlabel(self.x_value)
        self.ax.set_ylabel(self.y_value)
        
        x_array = self.data[self.x_value].values
        y_array = self.data[self.y_value].values
        
        self.ax.plot(x_array, y_array, '.')
        self.canvas.draw()
        
        
    def handler(self, item, column_no):

        x = self.x_value
        y = self.y_value
                
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph
        self.ax.clear()

        # plot data
        #ax.plot(self.data[x], self.data[y], '.')
       
        self.ax.set_xlabel(x)
        self.ax.set_ylabel(y)

        x_array = []
        y_array = []
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            if cur_item.checkState(0) == 0:
                x_array.append(float(cur_item.text(1)))
                y_array.append(float(cur_item.text(2)))
        
        x_array_chosen = []
        y_array_chosen = []
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            if cur_item.checkState(0) == 2:
                x_array_chosen.append(float(cur_item.text(1)))
                y_array_chosen.append(float(cur_item.text(2)))
                
                
        self.ax.plot(x_array, y_array, '.')
        self.ax.plot(x_array_chosen, y_array_chosen, color="orange", marker="o",linestyle='None', markersize = 5)
        
        x_chosen_point = float(item.text(1))
        y_chosen_point = float(item.text(2))
            
        self.ax.axhline(y=y_chosen_point, linestyle = "--")
        self.ax.axvline(x=x_chosen_point, linestyle = "--")
        
        self.ax.plot(x_chosen_point, y_chosen_point, color="r", marker="o", markersize = 5)
        
        self.canvas.draw()
        print("done")
    


    def loadData(self):
        self.treeWidget.clear()
        self.init_table()
        self.init_plot()
        self.treeWidget.setSortingEnabled(True)
        
    def reject(self):
        self.close()

                     

    def plottingButton(self):
        #self.dataTable.clear()
        x = self.x_value
        y = self.y_value
        
  
        #self.dataTable.setSortingEnabled(True)
                
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph
        self.ax.clear()
        
        try:
            os.remove(self.program_path +"/tmp_sens/percentiles_chart.csv")
            os.remove(self.program_path +"/tmp_sens/percentiles_chart_up.csv")
            os.remove(self.program_path +"/tmp_sens/percentiles_chart_down.csv")
        except:
            print("no percentiles charts")

        # plot all data
        #ax.plot(self.data[x], self.data[y], '.')
        
        self.ax.set_xlabel(x)
        self.ax.set_ylabel(y)

        # refresh canvas
        #self.canvas.draw()
        
        x_array = []
        y_array = []
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if item.checkState(0) == 0:
                x_array.append(float(item.text(1)))
                y_array.append(float(item.text(2)))
                
        x_array_chosen = []
        y_array_chosen = []
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            if cur_item.checkState(0) == 2:
                x_array_chosen.append(float(cur_item.text(1)))
                y_array_chosen.append(float(cur_item.text(2)))
        print(y_array_chosen)
                
        self.ax.plot(x_array, y_array, '.')
        self.ax.plot(x_array_chosen, y_array_chosen, color="orange", marker="o",linestyle='None', markersize = 5)
        
        
        #self.canvas.draw()
        
        # normal y array
        tmp_data = pd.DataFrame({x : x_array + x_array_chosen, y : y_array + y_array_chosen})
        tmp_data.to_csv(self.program_path + "/tmp_sens/cur_data.csv",  index=False)
        
        # up y array
        y_array_chosen_up = [float(self.Variation_up.text())*i for i in y_array_chosen]
        tmp_data = pd.DataFrame({x : x_array + x_array_chosen, y : y_array + y_array_chosen_up})
        tmp_data.to_csv(self.program_path + "/tmp_sens/cur_data_up.csv",  index=False)
        
        # down y array
        y_array_chosen_down = [float(self.Variation_down.text())*i for i in y_array_chosen]
        tmp_data = pd.DataFrame({x : x_array + x_array_chosen, y : y_array + y_array_chosen_down})
        tmp_data.to_csv(self.program_path + "/tmp_sens/cur_data_down.csv",  index=False)
        
#        self.fit_model(data_file = "./tmp_sens/cur_data.csv")
#        self.fit_model(data_file = "./tmp_sens/cur_data_up.csv", curve_label =self.Variation_up.text())
#        self.fit_model(data_file = "./tmp_sens/cur_data_down.csv", curve_label =self.Variation_down.text())
        manager = TaskManager()
        manager.command = self.command
        manager.cur_Mu = self.Mu.text()
        manager.cur_Sigma = self.Sigma.text() 
        manager.cur_Lambda = self.Lambda.text()
        manager.x_value = self.x_value
        manager.y_value = self.y_value
        manager.start_process()
        manager.resultsChanged.connect(self.plot_50_percentile)
        
        
        
    def plot_50_percentile(self):
        for plot_dat in ["/tmp_sens/percentiles_chart.csv", "/tmp_sens/percentiles_chart_up.csv", "/tmp_sens/percentiles_chart_down.csv"]:
            try:
                lms_chart = pd.read_csv(self.program_path + plot_dat, sep =',', encoding = "ISO-8859-1")
                self.ax.plot(lms_chart["x"].values, lms_chart["C50"].values, label = plot_dat)
                self.ax.legend()
                self.canvas.draw()
    
            except:
                print("error")
        
class TaskManager(QtCore.QObject):
    resultsChanged = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        
        self.program_path = os.path.dirname(sys.argv[0])
        
        self.popUp = PopUpProcess(self)
        
        self.m_processes = []
        self.number_process_running = 0
        self.process_id = 0 
        
        self.cur_Mu = "1"
        self.cur_Sigma = "0"
        self.cur_Lambda = "0"
        self.x_value = "x"
        self.y_value = "y"
        
        self.command = 'Rscript'
        self.path2script =  ['/R_model/perc_sens.R', '/R_model/perc_sens_up.R', '/R_model/perc_sens_down.R']
        self.DataFiles = ["/tmp_sens/cur_data.csv", "/tmp_sens/cur_data_up.csv", "/tmp_sens/cur_data_down.csv"]
 
#        self.path2script =  ['R_model/perc_sens.R']
#        self.DataFiles = ["./tmp_sens/cur_data.csv"]
        
    def start_process(self):  
        print("start....")
    
        self.popUp.onStart()
        self.popUp.show()
        
        self.command_arg_list = []
        self.args = [self.cur_Mu, self.cur_Sigma, self.cur_Lambda]
        self.config = [self.x_value, self.y_value]
      
        for i in range(0,len(self.path2script)):
            command_arg = [self.program_path + self.path2script[i]] + self.args + [self.program_path + self.DataFiles[i]] + self.config
            self.command_arg_list.append(command_arg)
            
        print(self.command_arg_list)
        self.run_parallel(self.command, self.command_arg_list)
        
                
    def run_parallel(self, command, command_arg_list):
        print(command_arg_list)
        for i, cmd_arg in enumerate(command_arg_list):
            print(cmd_arg)
            process = QtCore.QProcess(self)
            process.finished.connect(partial(self.onReadyReadStandardOutput, i, cmd_arg))
            process.start(command, cmd_arg, QtCore.QIODevice.ReadOnly)
            self.m_processes.append(process)
            self.number_process_running += 1
            print(self.number_process_running)
#            self.completed += 1.0/(self.dimension)*100/2
#            self.popUp.pbar.setValue(self.completed)
            
    def onReadyReadStandardOutput(self, i, cmd_arg):
        print("done.......")
        

#        print(i)
#        print(cmd_arg)
        self.number_process_running -= 1
        process = self.sender()
        print(str(process.readAllStandardOutput(), encoding = "utf-8"))
#        print(self.number_process_running)
        if self.number_process_running <= 0:
            print("finished.")
            self.resultsChanged.emit()
            self.popUp.onFinished()
            self.popUp.close()

    
        
        
    def saveChartButton(self):
        rows_list = [self.HEADERS[1:]]
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if item.checkState(0) == 2:
                row_j = [float(item.text(j)) for j in range(1,len(self.HEADERS))]
                #print(row_j)
                rows_list.append(row_j)
        
        df_table = pd.DataFrame(rows_list)
        df_table.to_csv(self.program_path +"/tmp_sens/cur_checked_data.csv",  index=False, header= False)
        
        self.filename_chart_checked = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
        if self.filename_chart_checked:
            #print(type(self.filename))
            shutil.copy2(self.program_path +"/tmp_sens/cur_checked_data.csv", self.filename_chart_checked)
            

#            
