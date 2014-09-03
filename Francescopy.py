# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 10:49:12 2014

@author: francesco
"""
import pandas as pd
import numpy as np
#pd.set_printoptions(max_rows=200, max_columns=10)

grants = pd.read_csv('/home/francesco/Dropbox/DSR/5Week/raw.csv')

columns = grants.columns
col = columns[26:]
a = columns[26:41].values
b = [ i.replace(".","") for i in a ]
names = [ i[:-1] for i in b ]
names[-4] = names[-4] + '*'
names.insert(0,'GrantId')

def shapeGrantInv(row, col, names):
    import numpy as np
    import pandas as pd

    grantid = row[0]
    investigators = row[col]

    invIds = investigators[::15]
    n_Inv = invIds.count().sum()

    dataframe = pd.DataFrame(np.zeros((n_Inv, len(names))), columns = names)

    for i in range(n_Inv):

        dataframe.iloc[i,0] = grantid
        dataframe.iloc[i,1:] = investigators[(i*15):(i*15)+15].values
    return dataframe

vertical = pd.DataFrame(np.zeros((1, len(names))), columns = names)

for i in range(grants.shape[0]):
    data = shapeGrantInv(grants.iloc[i,:],col,names)
    vertical = vertical.append(data, ignore_index = True)

vertical[1:].to_csv('vertical.csv')