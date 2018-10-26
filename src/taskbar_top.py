# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 09:26:56 2018

@author: Christian Winkler
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Task_Bar(QtGui.QMainWindow):    
    def __init__(self, mainWindow):
        super(Task_Bar, self).__init__() 
        
        ''' Menubar buttons'''        
        # Load
        openfileButton = QtGui.QAction("&Load Data", self)
        openfileButton.setStatusTip('Load data from csv file')
        openfileButton.triggered.connect(mainWindow.open_fileDialog)
        
        # Save
        saverefcurvButton = QtGui.QAction("&Save Reference Curves", self)
        saverefcurvButton.setStatusTip('Save reference curves as csv file')
        saverefcurvButton.triggered.connect(mainWindow.open_saveRefCurvDialog)
        
        savetableButton = QtGui.QAction("&Save Table", self)
        savetableButton.setStatusTip('Save table as csv file')
        savetableButton.triggered.connect(mainWindow.open_saveTableDialog)
        
        # About 
        aboutButton = QtGui.QAction("&About", self)
        aboutButton.setStatusTip('About RefCurv')
        aboutButton.triggered.connect(mainWindow.open_aboutRefCurv)
        
        # Model 
        modelfittingButton = QtGui.QAction("&Model Fitting", self)
        modelfittingButton.setStatusTip('Model Fitting')
        modelfittingButton.triggered.connect(mainWindow.open_ModelFitting)
        
        modelselectionButton = QtGui.QAction("&Model Selection - BIC", self)
        modelselectionButton.setStatusTip('Model Selection - BIC')
        modelselectionButton.triggered.connect(mainWindow.open_ModelSelection)
        
        modelselectioncvButton = QtGui.QAction("&Model Selection - CV", self)
        modelselectioncvButton.setStatusTip('Model Selection - CV')
        modelselectioncvButton.triggered.connect(mainWindow.open_ModelSelectionCV)
        
        sensitivityButton = QtGui.QAction("&Sensitivity Analysis", self)
        sensitivityButton.setStatusTip('Sensitivity Analysis')
        sensitivityButton.triggered.connect(mainWindow.open_SensitivityAnalysis)
        
        admodelfittingButton = QtGui.QAction("&Model Fitting (advanced)", self)
        admodelfittingButton.setStatusTip('Model Fitting (advanced)')
        admodelfittingButton.triggered.connect(mainWindow.open_AdModelFitting)
        
        rv_computationButton = QtGui.QAction("&Reverse Computation", self)
        rv_computationButton.setStatusTip('Reverse Computation')
        rv_computationButton.triggered.connect(mainWindow.open_rv_computation)
        
        modelComparison = QtGui.QAction("&Model Comparison", self)
        modelComparison.setStatusTip('Model Comparison')
        modelComparison.triggered.connect(mainWindow.open_modelComp)
        
        # Setting
        plotsettingButton = QtGui.QAction("&Plot Setting", self)
        plotsettingButton.setStatusTip('Plot Setting')
        plotsettingButton.triggered.connect(mainWindow.open_PlotSetting)
        plotsettingButton.setEnabled(False)
        
        outlierssettingButton = QtGui.QAction("&Outliers Setting", self)
        outlierssettingButton.setStatusTip('Outliers Setting')
        outlierssettingButton.triggered.connect(mainWindow.open_OutliersSetting)
        
        rpathButton = QtGui.QAction("&R path", self)
        rpathButton.setStatusTip('R path')
        rpathButton.triggered.connect(mainWindow.open_rpath)
        
        # calculator
        zscoreButton = QtGui.QAction("&Z-score calculator", self)
        zscoreButton.setStatusTip('Z-score calculator')
        zscoreButton.triggered.connect(mainWindow.open_ZscoreCalc)
        
        zpButton = QtGui.QAction("&Z-score/Percentile converter", self)
        zpButton.setStatusTip('Z-score/Percentile converter')
        zpButton.triggered.connect(mainWindow.open_zpConverter)
        
        # Example Data
        mcButton = QtGui.QAction("&Monte Carlo Experiment", self)
        mcButton.setStatusTip('Monte Carlo Experiment')
        mcButton.triggered.connect(mainWindow.open_mc_experiment)
        
        exAbdomButton = QtGui.QAction("&Example Abdom", self)
        exAbdomButton.setStatusTip('Example Abdom')
        exAbdomButton.triggered.connect(mainWindow.open_ExData_Abdom)
        
        DBButton = QtGui.QAction("&DB", self)
        DBButton.setStatusTip('DB')
        DBButton.triggered.connect(mainWindow.open_ExData_DB)
        
        exEchoButton = QtGui.QAction("&Example Echo", self)
        exEchoButton.setStatusTip('Example Echo')
        exEchoButton.triggered.connect(mainWindow.open_ExData_Echo)
        
        exEcho2Button = QtGui.QAction("&Example Echo 2", self)
        exEcho2Button.setStatusTip('Example Echo 2')
        exEcho2Button.triggered.connect(mainWindow.open_ExData_Echo_2)
        
        # PV Loop
        pvloopButton = QtGui.QAction("&PV Loop", self)
        pvloopButton.setStatusTip('PV Loop')
        pvloopButton.triggered.connect(mainWindow.open_pvloop)
        
        # Documentation 
        docButton = QtGui.QAction("&Documentation", self)
        docButton.setStatusTip('RefCurv documentation')
        #docButton.triggered.connect(self.open_docRefCurv)
        
        ''' Menubar'''
        mainMenu = mainWindow.menuBar()
        #fileMenu
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openfileButton)
        fileMenu.addSeparator()
        fileMenu.addAction(saverefcurvButton)
        fileMenu.addAction(savetableButton)
        # model
        modelMenu = mainMenu.addMenu('&Model')
        modelMenu.addAction(modelfittingButton)
        modelMenu.addSeparator()
        modelMenu.addAction(modelselectionButton)
        modelMenu.addAction(modelselectioncvButton)
        modelMenu.addSeparator()
        modelMenu.addAction(sensitivityButton)
        modelMenu.addSeparator()
        modelMenu.addAction(admodelfittingButton)
        modelMenu.addAction(rv_computationButton)
        modelMenu.addAction(modelComparison)
        # calculator
        calculatorMenu = mainMenu.addMenu('&Calculator')
        calculatorMenu.addAction(zscoreButton)
        calculatorMenu.addAction(zpButton)
        # setting
        settingMenu = mainMenu.addMenu('&Setting')
        settingMenu.addAction(plotsettingButton)
        settingMenu.addAction(outlierssettingButton)
        settingMenu.addAction(rpathButton)
        # example data
        exdataMenu = mainMenu.addMenu('&Examples')
        exdataMenu.addAction(mcButton)
        exdataMenu.addAction(exAbdomButton)
        exdataMenu.addAction(DBButton)
        exdataMenu.addAction(exEchoButton)
        exdataMenu.addAction(exEcho2Button)
        # PV Loop
        pluginMenu = mainMenu.addMenu('&Plug-In')
        pluginMenu.addAction(pvloopButton) 
        #helpMenu
        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(aboutButton)