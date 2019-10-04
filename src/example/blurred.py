# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 10:46:48 2019

@author: chris
"""

import pandas as pd
import numpy as np

data  = pd.read_csv( "test_data_kristina.csv",sep =',', encoding = "ISO-8859-1")

data_df = pd.DataFrame()
data_df["x"] = data["age [month]"]
data_df["y"] = data["EDV [ml]"] * np.random.uniform(0.5, 2.0)

data_df.to_csv("test_data_kristina_reverse.csv",sep =',', encoding = "ISO-8859-1")