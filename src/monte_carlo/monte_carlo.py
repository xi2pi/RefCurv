import numpy as np
import pandas as pd
import random
from scipy.special import gamma, erf
from scipy.stats import truncnorm


import scipy.stats as st
import matplotlib.pyplot as plt

def z_score(L, M, S, y):
    if L == 0:
        z = (1/S)*np.log(y/M)
    else:
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
    
#L = 1.1
#M = 100
#S = 0.1 
    
   
#mu, sigma = 0, 1 # mean and standard deviation
#z_values = truncnorm.rvs(-1/(L*S), np.inf, size=1000)
#s = np.array([y_value(L,M,S, i) for i in z_values])
#
#count, bins, ignored = plt.hist(s, density=True)
#plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *
#               np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
#         linewidth=2, color='r')
#plt.plot(bins,
#         linewidth=2, color='r')
#plt.show()

lms_chart = pd.read_csv("./test_percentiles_chart_21_08.csv",sep =',', encoding = "ISO-8859-1")

plt.plot(lms_chart["x"].values, lms_chart["C3"].values, "k")
plt.plot(lms_chart["x"].values, lms_chart["C10"].values, "k" )
plt.plot(lms_chart["x"].values, lms_chart["C25"].values, "k" )
plt.plot(lms_chart["x"].values, lms_chart["C50"].values, "k" , linewidth=3)
plt.plot(lms_chart["x"].values, lms_chart["C75"].values, "k" )
plt.plot(lms_chart["x"].values, lms_chart["C90"].values, "k" )
plt.plot(lms_chart["x"].values, lms_chart["C97"].values, "k" )

x_MC_values = []
y_MC_values = []

for i in range(0, len(lms_chart["x"].values)): 
    M = lms_chart["mu"].values[i]
    L = lms_chart["nu"].values[i]
    S = lms_chart["sigma"].values[i]
#    print(L,M,S)
    if L > 0:
        z_values = truncnorm.rvs(-1/(L*S), np.inf, size=1)
    else:
        z_values = truncnorm.rvs(-np.inf, -1/(L*S), size=1)
    s = np.array([y_value(L,M,S, i) for i in z_values])

    for j in s:
        #plt.plot(lms_chart["x"].values[i], j, '.', color = "r")
        x_MC_values.append(lms_chart["x"].values[i])
        y_MC_values.append(j)
        

plt.plot(x_MC_values, y_MC_values, '.', color = "r" )


plt.show()

result = pd.DataFrame(x_MC_values, y_MC_values)
result.to_csv("result.csv")