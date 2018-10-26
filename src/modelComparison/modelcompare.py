# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 14:00:30 2018

@author: Christian Winkler
"""
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

def gaussian(x, mu, sig):
    y = np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    y_max = 1/np.sqrt(2 * np.pi* np.power(sig, 2.))
    return y_max *y

def histogram_intersection(h1, h2, bins):
   bins = np.diff(bins)
   sm = 0
   for i in range(len(bins)):
       sm += min(bins[i]*h1[i], bins[i]*h2[i])
   return sm
   
fig, ax = plt.subplots(1, 1)

x = np.linspace(0, 10, 100)
ax.plot(x, gaussian(x, 5, 1), 'r-', lw=5, alpha=0.6, label='norm pdf')
ax.plot(x, gaussian(x, 5, 1), 'b-', lw=5, alpha=0.6, label='norm pdf')

histogram_intersection(gaussian(x, 5, 1),gaussian(x, 5, 1), x)
       
