''' Grant Kaggle Competition '''

os.chdir('PublicProjects/Grants')

import csv
import pandas as pd
import os

raw = pd.read_csv('data/starterFile.csv',sep = ',')
rawGrants = raw.loc[:,'Grant.Application.ID':'SEO.Percentage.5']
rawInvest = raw.iloc[:,27:]
rawInvest['Grant.Application.ID'] = raw['Grant.Application.ID']
rawInvest = rawInvest.drop('X', 1)

longInvest = pd.DataFrame()
for i in range(0,15):
    j = 15*i

    temp = list(rawInvest.columns[(j):(j+15)])
    temp.append(rawInvest.columns[225])

    tempFrame = rawInvest[temp]

    tempFrame.columns = ['PersonID','Role','Year.of.Birth','Country.of.Birth',
    'Home.Language','Dept.No','Faculty.No','With.PHD','No.Years.in.Uni',
    'Num.of.Successful.Grant','Num.of.Unsuccessful.Grant','Astar','A','B','C',
    'Grant.Application.ID'] 

    longInvest = pd.concat(objs = [longInvest, tempFrame], axis = 0)