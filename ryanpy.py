# Ryan's code

import pandas as pd
import numpy as np

def get_tables(filename = '/home/bobbruno/Downloads/DSR/Kaggle Grants/sourcedata/raw.csv'):
    df_raw = pd.read_csv(filename)
    del df_raw[df_raw.columns[-1]]
    df_grants = df_raw[df_raw.columns[:26]]
    investigator_columns = [df_raw[df_raw.columns[0:26] + df_raw.columns[26 + 15*i : 26 + 15 * (i+1)]] for i in range(len(df_raw.columns[26:])/15)]
    for table in investigator_columns:
        table.columns = df_raw.columns[0:26] + investigator_columns[0].columns
    investigators = pd.concat(investigator_columns)
    unique_investigators = investigators.drop_duplicates()
    return unique_investigators.sort('Grant.Application.ID') #[unique_investigators['Role.1'].isnull()==False].sort('Grant.Application.ID')

def munge_data(df_orig):
    df = df_orig.copy()
    del df['Person.ID.1']

    # Find the oldest investigator's birth date
    oldest = pd.DataFrame(df.groupby('Grant.Application.ID')['Year.of.Birth.1'].min())

    # Get the number of investigators for each role
    numRole = pd.get_dummies(df['Role.1'])
    numRole = pd.groupby(numRole, numRole.index)[numRole.columns].sum()
    numRole = pd.DataFrame(numRole, index = oldest.index)

    # Get the % of aussies
    numAussies = pd.get_dummies(df['Country.of.Birth.1'])
    numAussies = pd.groupby(numAussies, numAussies.index)[numAussies.columns].sum()
    # We just imputed all values with NaN (no country info) to zero
    prcAussies = pd.DataFrame((numAussies['Australia'] / numAussies.sum(axis = 1)).fillna(0),
                              index = oldest.index, columns = ['% Australians'])

    # Sum the # of published papers
    numPapers = df.groupby('Grant.Application.ID')['A..1', 'A.1',
                                                   'B.1', 'C.1',
                                                   'Number.of.Successful.Grant.1',
                                                   'Number.of.Unsuccessful.Grant.1'].sum()
    numPapers = pd.DataFrame(numPapers, index=oldest.index)

    # Get rid of everything we don't need
    # REMINDER - LATER COME BACK AND DEAL WITH DEPARTMENT, FACULTY, NO YEARS AT FACULTY, PHD, ETC
    df.drop(['A..1', u'A.1', u'B.1', u'C.1', u'Country.of.Birth.1', u'Dept.No..1', u'Faculty.No..1',
           u'Home.Language.1', u'No..of.Years.in.Uni.at.Time.of.Grant.1', u'Number.of.Successful.Grant.1',
           u'Number.of.Unsuccessful.Grant.1', u'Role.1', u'Sponsor.Code', u'With.PHD.1', u'Year.of.Birth.1',
           u'SEO.Code.4', u'SEO.Code.5', u'SEO.Code.1', u'SEO.Code.2', u'SEO.Code.3', u'RFCD.Code.1',
           u'RFCD.Code.2', u'RFCD.Code.3', u'RFCD.Code.4', u'RFCD.Code.5'], inplace = True, axis = 1)
    df.drop_duplicates(inplace = True)
    df.set_index('Grant.Application.ID', inplace=True)
    finalDf = pd.merge(df, oldest, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, numRole, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, prcAussies, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, numPapers, left_index = True, right_index = True)
    return finalDf
    
