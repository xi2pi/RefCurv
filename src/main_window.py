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
import matplotlib.image as mpimg

import os
import pandas as pd
import numpy as np
import shutil
import scipy.stats as st
import sys

# RefCurv modules
import helprefcurv
from treeitems import *
from modelfitting import *
from advanced_modelfitting import *
from modelselectionBIC import *
from modelselectionCV import *
from sensitivityanalysis import *
from settings import *
from settings_outliers import *
from zscore_calculator import *
from ZPconverter import *
from monte_carlo import *
from reverse_computation import *
from taskbar_top import *
from rpath import *
from modelcomparison import *
from diagnosis import *

# PlugIn
import plugin.pv_loop.pvloop as pvloop_plugin

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        # set program path
        #self.program_path = os.path.dirname(sys.argv[0])
        self.program_path = os.getcwd()
        print(self.program_path) 
        
        # clear temp folder
        #self.del_tmp()
        
        ''' Modules '''
        # creating instances for each feature
        self.modelFitter = ModelFitting(self)
        self.ModelSelectiondialog = ModelSelectionBIC(self)
        self.ModelSelectionCVdialog = ModelSelectionCV(self)
        self.SensitivityDialog = SensitvityAnalysis(self)
        
        self.modelComp = Model_Comparison(self)        
        #self.PlotSettingsDialog = PlotSettings(self)
        self.OutliersSettingsDialog = OutliersSettings(self)
        self.ZscoreCalculator = Zscore_calculator(self)
        self.ZPConverter = ZP_converter(self)
        self.admodelFitter = AdModelFitting(self)
        self.mc_experiment = Monte_Carlo(self)
        self.rv_computation = Reverese_Comp(self)
        self.diagnosis = Diagnosis(self)
        self.taskB = Task_Bar(self)
        self.aboutRefCurv = helprefcurv.AboutWindow()
        
        self.pvloop_window = pvloop_plugin.pvloop_window()
        
        self.rpa = r_path(self, self.modelFitter, self.ModelSelectiondialog, self.ModelSelectionCVdialog, self.SensitivityDialog, self.admodelFitter)
    
        ''' variables & flags'''
        self.plotting_flag = False
        self.refcurv_computed = False
        self.file_flag = False
        self.res_on_off = self.OutliersSettingsDialog.outlier_on.isChecked() 
        
        ''' GUI '''        
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        self.resize(1300, 800)
        self.center_window()
        
        pal = QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
        
        self.mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(self.mainWidget)
        
        # main orientation is horizontal
        self.mainLayout = QtGui.QHBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        # right side        
        self.vLayout = QtGui.QVBoxLayout()      
        
        # table (tree widget)
        self.treeWidget = QtGui.QTreeWidget()
        self.treeWidget.setHeaderLabels(["Data"])
        self.treeWidget.itemClicked.connect(self.click_on_point)
        
        self.mainLayout.addWidget(self.treeWidget)
        self.mainLayout.insertLayout(1, self.vLayout)
        
        # figure 
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.vLayout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.canvas.draw()
        self.nav = NavigationToolbar(self.canvas,self.canvas, coordinates=False)
        
        # layout grid
        self.gridLayout=QtGui.QGridLayout()
        self.vLayout.insertLayout(1, self.gridLayout)
        xLabel = QtGui.QLabel("x-axis")
        xLabel.setAlignment(QtCore.Qt.AlignCenter)
        yLabel = QtGui.QLabel("y-axis")
        yLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # combobox        
        self.xCombo = QtGui.QComboBox()
        self.xCombo.setStyleSheet("background-color:rgb(255,255,255)")
        self.yCombo = QtGui.QComboBox()
        self.yCombo.setStyleSheet("background-color:rgb(255,255,255)")
        self.xCombo.currentIndexChanged.connect(self.on_combobox_changed)
        self.yCombo.currentIndexChanged.connect(self.on_combobox_changed)
        
        # buttons
        self.plotButton = QtGui.QPushButton("Plot")
        clearButton = QtGui.QPushButton("Clear")
        
        # connecting buttons with functions        
        self.plotButton.clicked.connect(self.plot_data)
        clearButton.clicked.connect(self.clear_figure)
        
        # set the layout
        self.gridLayout.addWidget(xLabel, 1, 1)
        self.gridLayout.addWidget(yLabel, 2, 1)
        self.gridLayout.addWidget(self.xCombo, 1, 2)
        self.gridLayout.addWidget(self.yCombo, 2, 2)
        self.gridLayout.addWidget(self.plotButton, 4, 2)
        self.gridLayout.addWidget(clearButton, 4, 1)
        
        self.statusBar()
    
    # setting the window title for each feature with version number      
    def refcurv_version(self, rc_version):
        self.modelFitter.setWindowTitle('RefCurv ' + rc_version + ' - Model Fitting')
        self.admodelFitter.setWindowTitle('RefCurv ' + rc_version + ' - Model Fitting (advanced)')
        self.ModelSelectiondialog.setWindowTitle('RefCurv ' + rc_version + ' - Model Selection BIC')
        self.ModelSelectionCVdialog.setWindowTitle('RefCurv ' + rc_version + ' - Model Selection CV')
        self.SensitivityDialog.setWindowTitle('RefCurv ' + rc_version + ' - Sensitivity Analysis')
        self.OutliersSettingsDialog.setWindowTitle('RefCurv ' + rc_version + ' - Outlier Settings')
        #self.PlotSettingsDialog.setWindowTitle('RefCurv ' + rc_version + '- Plot Settings')
        self.ZPConverter.setWindowTitle('RefCurv ' + rc_version + ' - Z-score/Percentile converter')
        self.ZscoreCalculator.setWindowTitle('RefCurv ' + rc_version + ' - Z-score calculator')
        self.modelComp.setWindowTitle('RefCurv ' + rc_version + ' - Model comparison')
        self.rpa.setWindowTitle('RefCurv ' + rc_version + ' - R path')
        self.mc_experiment.setWindowTitle('RefCurv ' + rc_version + ' - Monte Carlo Experiment')
        self.rv_computation.setWindowTitle('RefCurv ' + rc_version + ' - Reverse Computation')
        self.pvloop_window.setWindowTitle('RefCurv ' + rc_version + ' - PV Loop Simulation')
        self.diagnosis.setWindowTitle('RefCurv ' + rc_version + ' - Diagnosis tool')        
        
        self.aboutRefCurv.setWindowTitle('RefCurv ' + rc_version + ' - About')
        self.aboutRefCurv.set_version(rc_version)     
     
    # center the window
    def center_window(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    # clear temp folder
    def del_tmp(self):
        try:
            os.remove(self.program_path + "/tmp/percentiles.png")
        except:
            print("no ./tmp/percentiles.png to remove")
        try:
            os.remove(self.program_path + "/tmp/percentiles_chart.csv")
        except:
            print("no ./tmp/percentiles_chart.csv to remove")
        try:
            os.remove(self.program_path + "/tmp/cur_data.csv")
        except:
            print("no ./tmp/cur_data.csv to remove")
        try:
            os.remove(self.program_path + "/tmp/res_chart.csv")
        except:
            print("no ./tmp/res_chart.csv to remove")
            
    ''' open instances '''
    # About window
    def open_aboutRefCurv(self):
        self.aboutRefCurv.show()
    
    # File dialog
    def open_fileDialog(self):
        self.plotting_flag = False
        self.load_chosen_data()
        if self.file_flag == True:
            self.data = self.current_data
            self.table_update()
            self.clear_figure()
            self.refcurv_computed = False
            
            self.xCombo.clear()
            self.yCombo.clear()
            
            self.xCombo.addItems(list(self.data.columns.values))
            self.yCombo.addItems(list(self.data.columns.values))
        else:
            print("no data chosen")
        
    # Save curves dialog
    def open_saveRefCurvDialog(self):
        if os.path.isfile(self.program_path +"/tmp/percentiles_chart.csv"):
            try:
                filename_chart = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
                if filename_chart:
                    shutil.copy2(self.program_path +"/tmp/percentiles_chart.csv", filename_chart)
            except:
                print("copy error")
        else:
            print("no reference curves")
            
    # Save table dialog
    def open_saveTableDialog(self):
        my_list = []
        if self.file_flag == True:
            for i in range(self.treeWidget.topLevelItemCount()):
                item = self.treeWidget.topLevelItem(i)
                if item.checkState(0) == 2:
                    row_list = [item.text(i) for i in range(1,len(list(self.data))+1)]
                    my_list.append(row_list)
            df = pd.DataFrame(my_list, columns=list(self.data))
            df.to_csv(self.program_path + "/tmp/cur_table.csv", sep = ',', encoding = "ISO-8859-1", index = False)
            
            filename_table = QtGui.QFileDialog.getSaveFileName(self,'Save File', ' ','*.csv')
            if filename_table:
                shutil.copy2(self.program_path +"/tmp/cur_table.csv", filename_table)
        else:
            print("no data chosen")
          
    # Model fitting dialog
    def open_ModelFitting(self):
        if self.plotting_flag == True:
            # Pass table and chosen data points to model fitting
            x_value = self.xCombo.currentText()
            y_value = self.yCombo.currentText()
            
            x_array = []
            y_array = []
            for i in range(self.treeWidget.topLevelItemCount()):
                cur_item = self.treeWidget.topLevelItem(i)
                if cur_item.checkState(0) == 2:
                    x_array.append(float(cur_item.text(self.xCombo.currentIndex()+1)))
                    y_array.append(float(cur_item.text(self.yCombo.currentIndex()+1)))
            tmp_data = pd.DataFrame({x_value : x_array, y_value : y_array})
            tmp_data = tmp_data[[x_value, y_value]]
            tmp_data.to_csv(self.program_path + "/tmp/cur_data.csv",  index=False)
            
            # defining attributes for model fitting
            self.modelFitter.figure = self.figure
            self.modelFitter.canvas = self.canvas
            self.modelFitter.chosen_xAxis = self.xCombo.currentText()
            self.modelFitter.chosen_yAxis = self.yCombo.currentText()
            self.modelFitter.res_limit_up = self.OutliersSettingsDialog.outlier_limit_up
            self.modelFitter.res_limit_low = self.OutliersSettingsDialog.outlier_limit_low
            
            # Show dialog
            self.modelFitter.show()
            self.modelFitter.activateWindow()
    
    # Advanced model fitting dialog (similar to standard model fitting)        
    def open_AdModelFitting(self):
        if self.plotting_flag == True:
            # Pass table and chosen data points to model fitting
            x_value = self.xCombo.currentText()
            y_value = self.yCombo.currentText()
    
            x_array = []
            y_array = []
            for i in range(self.treeWidget.topLevelItemCount()):
                cur_item = self.treeWidget.topLevelItem(i)
                if cur_item.checkState(0) == 2:
                    x_array.append(float(cur_item.text(self.xCombo.currentIndex()+1)))
                    y_array.append(float(cur_item.text(self.yCombo.currentIndex()+1)))
            tmp_data = pd.DataFrame({x_value : x_array, y_value : y_array})
            tmp_data = tmp_data[[x_value, y_value]]
            tmp_data.to_csv(self.program_path + "/tmp/cur_data.csv",  index=False)
            
            # defining attributes for model fitting
            self.admodelFitter.figure = self.figure
            self.admodelFitter.canvas = self.canvas
            self.admodelFitter.chosen_xAxis = self.xCombo.currentText()
            self.admodelFitter.chosen_yAxis = self.yCombo.currentText()
            self.admodelFitter.res_limit_up = self.OutliersSettingsDialog.outlier_limit_up
            self.admodelFitter.res_limit_low = self.OutliersSettingsDialog.outlier_limit_low
            
            # Show dialog
            self.admodelFitter.show()
            self.admodelFitter.activateWindow()
            
    def open_diagnosis(self):
        self.diagnosis.plot_residuals()
        self.diagnosis.show()
        
    def open_ZscoreCalc(self):
        self.ZscoreCalculator.show()
        
    def open_zpConverter(self):
        self.ZPConverter.show()

    # BIC model selection dialog
    def open_ModelSelection(self):
        if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
            self.ModelSelectiondialog.x_value = self.xCombo.currentText()
            self.ModelSelectiondialog.y_value = self.yCombo.currentText()
            self.ModelSelectiondialog.fileName = self.program_path +  "/tmp/cur_data.csv"
            self.ModelSelectiondialog.show()
        else:
            print("choose data")
    
    # CV model selection dialog
    def open_ModelSelectionCV(self):
        if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
            self.ModelSelectionCVdialog.x_value = self.xCombo.currentText()
            self.ModelSelectionCVdialog.y_value = self.yCombo.currentText()
            self.ModelSelectionCVdialog.fileName = self.program_path +  "/tmp/cur_data.csv"
            self.ModelSelectionCVdialog.show()
        else:
            print("choose data")
            
    # Sensitivity analysis dialog
    def open_SensitivityAnalysis(self):
        if os.path.isfile(self.program_path + "/tmp/cur_data.csv"):
            my_data = pd.read_csv(self.program_path + "/tmp/cur_data.csv",sep =',', encoding = "ISO-8859-1")
            
            self.SensitivityDialog.data = my_data
            self.SensitivityDialog.figure.clear()
            self.SensitivityDialog.x_value = self.xCombo.currentText()
            self.SensitivityDialog.y_value = self.yCombo.currentText()
            
            self.SensitivityDialog.loadData()
            self.SensitivityDialog.show()
        else:
            print("choose data")
     
    def open_rv_computation(self):       
        self.rv_computation.show()
        
    def open_modelComp(self):    
        self.modelComp.show()
            
    def open_mc_experiment(self):
        self.mc_experiment.show()
        
    def open_ExData_Abdom(self):
        self.load_example(self.program_path +"/example/test_data_abdom.csv")
    
    def open_ExData_DB(self):
        self.load_example(self.program_path +"/example/db.csv")
    
    def open_ExData_Echo(self):
        self.load_example(self.program_path +"/example/test_data_kristina.csv")
        
    def open_ExData_Echo_2(self):
        self.load_example(self.program_path +"/example/test_data_wolf.csv")
        
    #def open_PlotSetting(self):
    #    self.PlotSettingsDialog.show()
    
    def open_OutliersSetting(self):
        self.OutliersSettingsDialog.show()
        
    def open_rpath(self):       
        self.rpa.show()
        
    def open_pvloop(self):
        self.pvloop_window.show()
        
    ''' table & plotting '''
    # Clear figure
    def clear_figure(self):
        self.ax.clear()
        self.canvas.draw()
        self.plotButton.setEnabled(True)
        self.xCombo.setEnabled(True)
        self.yCombo.setEnabled(True)
        self.refcurv_computed = False
        self.del_tmp()
        for i in range(self.treeWidget.topLevelItemCount()):
            self.treeWidget.topLevelItem(i).unhide_item()
            
    # Disable the data point selection in the table
    def disable_table(self):
        for i in range(self.treeWidget.topLevelItemCount()):
            self.treeWidget.topLevelItem(i).hide_item()
        
    # Update table after data has been loaded into RefCurv
    def table_update(self):
        self.treeWidget.clear()
        self.headers = [" "] + list(self.data) + ["Residuals"]
        self.treeWidget.setColumnCount(len(self.headers))
        self.treeWidget.setHeaderLabels(self.headers)
 
        dataList = self.data.values.tolist()
        for i in range(0, len(dataList)):
            item = CustomTreeItem(self.treeWidget, dataList[i])
            item.setData(len(list(self.data))+1, Qt.EditRole, "-")
        
        self.treeWidget.setSortingEnabled(True)
        
        # Set Columns Width to match content:
        for column in range(self.treeWidget.columnCount()):
            self.treeWidget.resizeColumnToContents(column)
            
    # Plotting data
    def plot_data(self):
        self.plotting_flag = True
        
        # get current dependent and independent variable
        x = self.xCombo.currentText()
        y = self.yCombo.currentText()
        
        # define figure
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        
        self.ax.xaxis.set_tick_params(labelsize=12)
        self.ax.yaxis.set_tick_params(labelsize=12)
        
        self.ax.set_xlabel(x, fontsize=16)
        self.ax.set_ylabel(y, fontsize=16)
        
        # data arrays
        self.x_array = []
        self.y_array = []
        
        mask_chosen_data = np.ones(self.treeWidget.topLevelItemCount(),dtype=bool)
        
        # get chosen data points
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)
            if item.checkState(0) == 2:
                mask_chosen_data[i] = False
                self.x_array.append(float(item.text(self.xCombo.currentIndex()+1)))
                self.y_array.append(float(item.text(self.yCombo.currentIndex()+1)))
            
        # plot data
        #self.ax.plot(self.x_array, self.y_array, '.', color = "#1f77b4ff")
        self.ax.plot(self.x_array, self.y_array, '.')
        # set figure limits
        x_array_diff = 0.05*(max(self.x_array) - min(self.x_array))
        y_array_diff = 0.05*(max(self.y_array) - min(self.y_array))
        
        self.ax.set_xlim(min(self.x_array)-x_array_diff, max(self.x_array)+x_array_diff*2)
        self.ax.set_ylim(min(self.y_array)-y_array_diff, max(self.y_array)+y_array_diff*2)
            
        # plot reference curves
        if self.refcurv_computed == True:
            self.plot_refcurv()
            self.plot_outlier(self.x_array, self.y_array)
            self.canvas.draw()
        else:
            self.canvas.draw()
        print("done")
        
        # save data in tmp folder
        tmp_data = pd.DataFrame({x : self.x_array, y : self.y_array})
        tmp_data = tmp_data[[x, y]]
        tmp_data.to_csv(self.program_path + "/tmp/cur_data.csv",  index=False)
        
    # click on data point and highlight it
    def click_on_point(self, item, column_no):
        if self.refcurv_computed == True:           
            print("refcurv present")
            self.click_on_point_ref(item, column_no)
        else:
            self.click_on_point_no_ref(item, column_no)
    
    # click on data point - reference curve computed     
    def click_on_point_ref(self, item, column_no):
            x_value = self.xCombo.currentText()
            y_value = self.yCombo.currentText()

            self.ax.clear()
    
            self.ax.set_xlabel(x_value, fontsize=16)
            self.ax.set_ylabel(y_value, fontsize=16)
            
            self.ax.xaxis.set_tick_params(labelsize=12)
            self.ax.yaxis.set_tick_params(labelsize=12)
            
            self.ax.plot(self.x_array, self.y_array, '.', color = "#1f77b4ff")
        
            x_array_diff = 0.05*(max(self.x_array) - min(self.x_array))
            y_array_diff = 0.05*(max(self.y_array) - min(self.y_array))
            
            self.ax.set_xlim(min(self.x_array)-x_array_diff, max(self.x_array)+x_array_diff*2)
            self.ax.set_ylim(min(self.y_array)-y_array_diff, max(self.y_array)+y_array_diff*2)
            
            self.plot_refcurv()
            self.plot_outlier(self.x_array, self.y_array)
            
            x_chosen_point = float(item.text(self.xCombo.currentIndex()+1))
            y_chosen_point = float(item.text(self.yCombo.currentIndex()+1))
            
            if item.checkState(0) == 2:
                self.ax.axhline(y=y_chosen_point, linestyle = "--")
                self.ax.axvline(x=x_chosen_point, linestyle = "--")
                  
                self.ax.plot(x_chosen_point, y_chosen_point, color="r", marker="o", markersize = 5)  
            else:
                print("not chosen")
            self.canvas.draw() 
            
    # click on data point - reference curve not computed  
    def click_on_point_no_ref(self, item, column_no):
        if self.plotting_flag == True:
            print("x :" + str(float(item.text(self.xCombo.currentIndex()+1))))
            print("y: " + str(float(item.text(self.yCombo.currentIndex()+1))))
            
            x_value = self.xCombo.currentText()
            y_value = self.yCombo.currentText()

            self.ax.clear()
    
            self.ax.set_xlabel(x_value, fontsize=16)
            self.ax.set_ylabel(y_value, fontsize=16)
                        
            self.ax.xaxis.set_tick_params(labelsize=12)
            self.ax.yaxis.set_tick_params(labelsize=12)
    
            x_array = []
            y_array = []
            for i in range(self.treeWidget.topLevelItemCount()):
                cur_item = self.treeWidget.topLevelItem(i)
                if cur_item.checkState(0) == 2:
                    x_array.append(float(cur_item.text(self.xCombo.currentIndex()+1)))
                    y_array.append(float(cur_item.text(self.yCombo.currentIndex()+1)))
                    
            self.ax.plot(x_array, y_array, '.', color = "#1f77b4ff")
            
            x_array_diff = 0.05*(max(x_array) - min(x_array))
            y_array_diff = 0.05*(max(y_array) - min(y_array))
            
            self.ax.set_xlim(min(x_array)-x_array_diff, max(x_array)+x_array_diff*2)
            self.ax.set_ylim(min(y_array)-y_array_diff, max(y_array)+y_array_diff*2)
            
            x_chosen_point = float(item.text(self.xCombo.currentIndex()+1))
            y_chosen_point = float(item.text(self.yCombo.currentIndex()+1))
            if item.checkState(0) == 2:
                self.ax.axhline(y=y_chosen_point, linestyle = "--")
                self.ax.axvline(x=x_chosen_point, linestyle = "--")
                  
                self.ax.plot(x_chosen_point, y_chosen_point, color="r", marker="o", markersize = 5)
            else:
                print("not chosen")
            
            self.canvas.draw()
                
            tmp_data = pd.DataFrame({x_value : x_array, y_value : y_array})
            tmp_data = tmp_data[[x_value, y_value]]
            tmp_data.to_csv(self.program_path + "/tmp/cur_data.csv",  index=False)
            print("done")
        else:
            print("plotting is turned off")
            
    ''' Plotting reference curves '''
    def plot_refcurv(self):
        lms_chart = pd.read_csv(self.program_path + "/tmp/percentiles_chart.csv" ,sep =',', encoding = "ISO-8859-1")
        try:
            self.ax.plot(lms_chart["x"].values, lms_chart["C3"].values, "k")
            self.ax.plot(lms_chart["x"].values, lms_chart["C10"].values, "k" )
            self.ax.plot(lms_chart["x"].values, lms_chart["C25"].values, "k" )
            self.ax.plot(lms_chart["x"].values, lms_chart["C50"].values, "k" , linewidth=3)
            self.ax.plot(lms_chart["x"].values, lms_chart["C75"].values, "k" )
            self.ax.plot(lms_chart["x"].values, lms_chart["C90"].values, "k" )
            self.ax.plot(lms_chart["x"].values, lms_chart["C97"].values, "k" )
            
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C3"].values[-1], "P3", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C10"].values[-1], "P10", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C25"].values[-1], "P25", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C50"].values[-1], "P50", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C75"].values[-1], "P75", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C90"].values[-1], "P90", size = 12)
            self.ax.text(lms_chart["x"].values[-1]*1.01, lms_chart["C97"].values[-1], "P97", size = 12)
     
        except:
            print("refcurv plotting error")
            
    ''' Outliers '''
    # set outlier detection on/off
    def set_Outlier(self):
        self.res_on_off = self.OutliersSettingsDialog.outlier_on.isChecked()
        self.OutliersSettingsDialog.close()
        if self.refcurv_computed == True:
            self.ax.clear()
            self.plot_data()
            self.plot_outlier(self.x_array, self.y_array)
            self.canvas.draw()
    
    # defining and entering the residuum into the table
    def mark_outlier(self):
        self.treeWidget.setSortingEnabled(False)
        res = pd.read_csv(self.program_path + "/tmp/res_chart.csv",sep =',', encoding = "ISO-8859-1")
        counter_i = 0
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            cur_item.setData(len(list(self.data))+1, Qt.EditRole, "-")
            
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            if cur_item.checkState(0) == 2:
                cur_item.setData(len(list(self.data))+1, Qt.EditRole, str(round(res["resid_m1"].values[counter_i],4)))
                counter_i += 1
            else:
                cur_item.setData(len(list(self.data))+1, Qt.EditRole, "-")
        self.treeWidget.setSortingEnabled(True)
    
    # highlight outliers in the figure              
    def plot_outlier(self, x_array, y_array):
        if self.res_on_off == True:
            res = pd.read_csv(self.program_path + "/tmp/res_chart.csv",sep =',', encoding = "ISO-8859-1")
            
            residuals = res["resid_m1"].values
            
            # get upper and lower limit from the dialog
            upper = st.norm.ppf(float(self.OutliersSettingsDialog.outlier_limit_up_edit.text())/100)
            lower = st.norm.ppf(float(self.OutliersSettingsDialog.outlier_limit_low_edit.text())/100)
            
            print(upper)
            print(lower)
            
            # define outliers
            y_upper = np.ma.masked_where(residuals < upper, y_array)
            y_lower = np.ma.masked_where(residuals > lower, y_array)
            y_middle = np.ma.masked_where(np.logical_or(residuals < lower, residuals > upper), y_array)
            
            # plot outlier
            self.ax.plot(x_array, y_upper, '.', color='y')
            self.ax.plot(x_array, y_lower, '.', color='y')
            self.ax.plot(x_array, y_middle, '.', color = "#1f77b4ff")
            print("outliers plotted")
        else:
            print("outlier detection off")
        
    ''' changing dependent and independent variables ''' 
    def on_combobox_changed(self):
        self.refcurv_computed = False
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            for j in range(0,len(list(self.data))+1):
                cur_item.setBackgroundColor(j,QtGui.QColor('white'))
            
        for i in range(self.treeWidget.topLevelItemCount()):
            cur_item = self.treeWidget.topLevelItem(i)
            
            clr = QtGui.QColor(51,153,255)
            cur_item.setBackgroundColor(self.xCombo.currentIndex()+1, clr)
            cur_item.setBackgroundColor(self.yCombo.currentIndex()+1, clr)
            
    ''' loading data '''        
    def load_chosen_data(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self,'Open File', ' ','*.csv')
        if self.filename:
            try:
                self.current_data = pd.read_csv(self.filename,sep =',', encoding = "ISO-8859-1")
                print(self.current_data)
                self.file_flag = True
            except:
                print("reading error - chosen data file")
                self.file_flag = False
                
    def load_example(self, example_file):
        # loading example datasets
        self.plotting_flag = False
        print(example_file)
        try:
            self.current_data = pd.read_csv(example_file, sep =',', encoding = "ISO-8859-1")
            print(self.current_data)
            self.file_flag = True
            self.data = self.current_data

            self.table_update()
            self.clear_figure()
            self.refcurv_computed = False
            
            self.xCombo.clear()
            self.yCombo.clear()
            
            self.xCombo.addItems(list(self.data.columns.values))
            self.yCombo.addItems(list(self.data.columns.values))

        except:
            print("reading error - example")
            self.file_flag = False
        
