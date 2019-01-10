import numpy as np
import pandas as pd
import random
from scipy.special import gamma, erf
from scipy.stats import truncnorm
from scipy.optimize import minimize


import scipy.stats as st
import matplotlib.pyplot as plt

def z_score(L, M, S, y):
#    if L == 0:
#        z = (1/S)*np.log(y/M)
#    else:
    z = (1/(S*L))*(((y/M)**L)-1)
    return z
    
def y_value(L, M, S, z):
    if L == 0:
        y = M*np.exp(S * z)
    else:
        y = M*(1 + L * S * z)**(1/L)
    return y
    
def BCCG(params,x):
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
    
def p2z(value):
    return st.norm.ppf(value)
    
def z2p(value):
    return st.norm.cdf(value)
    

#distance = np.abs(y[4]-y[3]) - np.abs(y[3]-y[2])

#symmetry check
#if distance > 0.001:
#    print("true")
    #z = (1/(S*L))*(((y/M)**L)-1)

def error_func(para, y):
    L = para[0]
    M = para[1]
    S = para[2]
    
    if L == 0:
        error = np.inf
    else:
            
        
        z_values = p2z(np.array([0.03, 0.1, 0.25, 0.5, 0.75, 0.9, 0.97]))
        try:
            y_comp = y_value(L, M, S, z_values)
            error = np.sum(np.abs(y - y_comp))
        except:
            error = np.inf
    return error
    
lms_chart = pd.read_csv("./test_percentiles_chart_21_08.csv",sep =',', encoding = "ISO-8859-1")

M_array = []
L_array = []
S_array = []

y_0 = np.array([lms_chart[i].values[0] for i in ["C3", "C10", "C25", "C50", "C75", "C90", "C97"]])
para_start = [-0.4, y_0[3], 0.35]
for j in range(0, len(lms_chart["x"].values)):
    x = lms_chart["x"].values[j]
    y = np.array([lms_chart[i].values[j] for i in ["C3", "C10", "C25", "C50", "C75", "C90", "C97"]])
        
    res = minimize(error_func, para_start, args = (y), method='nelder-mead') 
    M_array.append(res.x[1])
    L_array.append(res.x[0])
    S_array.append(res.x[2])
    para_start = [res.x[0], res.x[1], res.x[2]]
    
plt.figure()
plt.plot(lms_chart["x"].values, lms_chart["mu"].values, 'r')
plt.plot(lms_chart["x"].values, M_array, 'b')
plt.title("M")
plt.show()

plt.figure()
plt.plot(lms_chart["x"].values, lms_chart["nu"].values, 'r')
plt.plot(lms_chart["x"].values, L_array, 'b')
plt.title("L")
plt.show()

plt.figure()
plt.plot(lms_chart["x"].values, lms_chart["sigma"].values, 'r')
plt.plot(lms_chart["x"].values, S_array, 'b')
plt.title("S")
plt.show()
     
#print(error_func(2,1,2,y))
    
    
    
    
    
#plt.plot(lms_chart["x"].values, lms_chart["C3"].values, "k")
#plt.plot(lms_chart["x"].values, lms_chart["C10"].values, "k" )
#plt.plot(lms_chart["x"].values, lms_chart["C25"].values, "k" )
#plt.plot(lms_chart["x"].values, lms_chart["C50"].values, "k" , linewidth=3)
#plt.plot(lms_chart["x"].values, lms_chart["C75"].values, "k" )
#plt.plot(lms_chart["x"].values, lms_chart["C90"].values, "k" )
#plt.plot(lms_chart["x"].values, lms_chart["C97"].values, "k" )

