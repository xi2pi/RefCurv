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
import subprocess
import pandas as pd
import numpy as np
import sys

import scipy.stats as st
from scipy.special import gamma, erf


class Diagnosis(QtGui.QDialog):    
    def __init__(self, mainWindow):
        super(Diagnosis, self).__init__() 
        #self.program_path = os.path.dirname(sys.argv[0])
        self.program_path = os.getcwd()


        # GUI      
        self.setWindowIcon(QIcon(self.program_path +'/logo/refcurv_logo.png'))
        
        # figure 
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('pick_event', self.onpick)

        self.ax1 = self.figure.add_subplot(221)
        self.ax2 = self.figure.add_subplot(222)
        self.ax3 = self.figure.add_subplot(223)
        self.ax4 = self.figure.add_subplot(224)
        self.canvas.draw()
        self.nav = NavigationToolbar(self.canvas,self.canvas, coordinates=False)
 
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.canvas)

        self.setLayout(mainLayout)
        
        self.lms_diagnosis()
        
    def BCCG(self, params,x):
        M = params[0]
        S = params[1]
        L = params[2]
        
        Phi = 0.5*(1 + erf((1/(S*np.abs(L)))/(np.sqrt(2))))
        
        if L == 0:
            z = (1/S)*np.log(x/M)
        else:
            z = (1/(S*L))*(((x/M)**L)-1)
        
        f = (x**(L-1)*np.exp(-0.5*z**2))/((M**L)*S*Phi*np.sqrt(2*np.pi))
        return f
      
    
    def LL(self, params, x):
        #if (params[0]>0 and params[1]>0):
        try:
            prob = 0
            prob_i = self.BCCG(params, x)
            prob = np.sum(np.log(prob_i))


            return -prob
        except:
            return np.inf
        
    def lms_diagnosis(self):
        
        self.LMS_diagnosis_window = QtGui.QDialog()
        
        self.figure_lms = Figure()
        self.canvas_lms = FigureCanvas(self.figure_lms)

        self.ax1_lms = self.figure_lms.add_subplot(221)
        self.ax2_lms = self.figure_lms.add_subplot(222)
        self.ax3_lms = self.figure_lms.add_subplot(223)
        self.ax4_lms = self.figure_lms.add_subplot(224)
        
        
        self.canvas_lms.draw()
        
         
        mainLayout_lms = QtGui.QVBoxLayout()
        mainLayout_lms.addWidget(self.canvas_lms)

        self.LMS_diagnosis_window.setLayout(mainLayout_lms)
        
        
    def update_lms_diagnosis(self):
        self.ax1_lms.clear()
        self.ax2_lms.clear()
        self.ax3_lms.clear()
        
        variation_vector = np.arange(0.5, 1.5, 0.01)
        
        cur_L = self.cur_data["nu"].values[self.index_data]
        cur_M = self.cur_data["mu"].values[self.index_data]
        cur_S = self.cur_data["sigma"].values[self.index_data]
        
        cur_x = self.cur_data.iloc[:,1].values[self.index_data]
        
        L_variation = variation_vector * cur_L
        M_variation = variation_vector * cur_M
        S_variation = variation_vector * cur_S
        
        likelihood_matrix = np.zeros((len(variation_vector), len(variation_vector)))
        
        print(cur_x)
        
        
        ######### fix L
        for l in [cur_L]:
        
            for i in range(0,len(M_variation)):
                for j in range(0,len(S_variation)):
                    parameter = [M_variation[i], S_variation[j], l[0]]
                    
                    try:
                        likelihood_matrix[i,j] = self.LL(parameter, cur_x)
                    except:
                        likelihood_matrix[i,j] = np.inf
                
                
        m_variation, s_variation = np.meshgrid(M_variation, S_variation)
            
        print(likelihood_matrix)
        test = self.ax1_lms.contourf(m_variation, s_variation, likelihood_matrix)
        
        self.ax1_lms.set_title("L = " + str(l))
        self.ax1_lms.set_ylabel("S")
        self.ax1_lms.set_xlabel("M")
        self.ax1_lms.plot(cur_M, cur_S,"ro")
        
        cbar = self.figure_lms.colorbar(test)
        #self.colorbar = self.figure_lms.colorbar(self.ax1_lms, ax=self.ax1_lms)
        
        ########### fix S
        for s in [cur_S]:
        
            for i in range(0,len(M_variation)):
                for j in range(0,len(L_variation)):
                    parameter = [M_variation[i], s[0], L_variation[j]]

                    try:
                        likelihood_matrix[i,j] = self.LL(parameter, cur_x)
                    except:
                        likelihood_matrix[i,j] = np.inf
                
                
        m_variation, l_variation = np.meshgrid(M_variation, L_variation)
            
        self.ax2_lms.contourf(m_variation, l_variation, likelihood_matrix)
        
        self.ax2_lms.set_title("S = " + str(s))
        self.ax2_lms.set_ylabel("L")
        self.ax2_lms.set_xlabel("M")
        self.ax2_lms.plot(cur_M, cur_L,"ro")
        
        ########### fix M
        for m in [cur_M]:
        
            for i in range(0,len(S_variation)):
                for j in range(0,len(L_variation)):
                    parameter = [m[0], S_variation[i], L_variation[j]]

                    try:
                        likelihood_matrix[i,j] = self.LL(parameter, cur_x)
                    except:
                        likelihood_matrix[i,j] = np.inf
                
                
        s_variation, l_variation = np.meshgrid(S_variation, L_variation)
            
        self.ax3_lms.contourf(s_variation, l_variation, likelihood_matrix)
        
        self.ax3_lms.set_title("M = " + str(m))
        self.ax3_lms.set_ylabel("L")
        self.ax3_lms.set_xlabel("S")
        self.ax3_lms.plot(cur_S, cur_L,"ro")
        
    
        self.canvas_lms.draw()
        self.LMS_diagnosis_window.show()

        
    def onpick(self, event):
        try:
            thisdata = event.artist
            #xdata = thisdata.get_xdata()
            #ydata = thisdata.get_ydata()
            
            self.index_data = event.ind
            
            print(self.index_data)
            print(self.cur_data.iloc[:,0].values[self.index_data], self.cur_data.iloc[:,1].values[self.index_data])
            
            self.update_lms_diagnosis()
        except:
            print("error picking")
        #print('index: %d\nobjective 1: %0.2f\nobjective 2: %0.2f\nobjective' % (event.ind[0], self.cur_data[ind,0], self.cur_data[ind,1]))

        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
#              ('double' if event.dblclick else 'single', event.button,
#               event.x, event.y, event.xdata, event.ydata))
               
        #self.ax4.plot(event.xdata, event.ydata,  color="r", marker="o", markersize = 5) 
        #self.canvas.draw()
        
    def plot_residuals(self):
        try:
            self.cur_data = pd.read_csv(self.program_path + "/tmp/cur_data.csv",sep =',', encoding = "ISO-8859-1")
            lms_datapoint_chart = pd.read_csv(self.program_path + "/tmp/lms_datapoint_chart.csv",sep =',', encoding = "ISO-8859-1")
            res = pd.read_csv(self.program_path + "/tmp/res_chart.csv",sep =',', encoding = "ISO-8859-1")
            
            self.cur_data = self.cur_data.join(lms_datapoint_chart)
            self.cur_data = self.cur_data.join(res["resid_m1"])
            #print(cur_data)
            
            residuals = np.sort(res["resid_m1"].values)
            residuals_index = np.arange(len(residuals))
            residuals_theoretical = st.norm.ppf(residuals_index/len(residuals))
            
            # 1. plot
            self.ax1.plot(residuals_theoretical, residuals, '.', picker = 5)
            self.ax1.set_title("Normal Q-Q plot")
            self.ax1.set_ylabel("Sample quantiles")
            self.ax1.set_xlabel("Theoretical quantiles")
            # 2. plot
            self.ax2.plot(residuals_theoretical, residuals-residuals_theoretical, '.', picker = 5)
            self.ax2.set_title("Worm plot")
            self.ax2.set_ylabel("Deviation")
            self.ax2.set_xlabel("Unit normal quantile")
            
            # 3. plot
            num_bins = 20
            self.ax3.hist(residuals, num_bins, normed=1, picker = 5)
            self.ax3.set_title("Density estimate")
            self.ax3.set_ylabel("Density")
            self.ax3.set_xlabel("Quantile residuals")
            
            
            k2, p = st.normaltest(residuals)
            alpha = 1e-3
            print("p = {:g}".format(p))
            
            # 4. plot
            
            self.ax4.plot(self.cur_data.iloc[:,0].values, residuals,'.', picker = 5)
            self.ax4.set_title("Against fitted values")
            self.ax4.set_ylabel("Quantile residuals")
            self.ax4.set_xlabel("Fitted values")
            
            self.canvas.draw()
        except:
            print("error")