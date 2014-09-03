# Ryan's code

import pandas as pd
import numpy as np
import time, datetime
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import chi2, SelectKBest, f_classif
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.svm import LinearSVC

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

def combine_columns(dfOrig, codeName = 'SEO.Code.', prcName = 'SEO.Percentage.', codeRange = 5, index = 'Grant.Application.ID'):
    """ Goes through all codeNames + codeRange, , impute '99' to blanks, get_dummies on them, drops colums with code 0 and
    add up each throughout the range."""
    df = dfOrig.copy()
    cleanDf = df[['{}{}'.format(codeName, i) for i in range(1, codeRange+1)]].fillna(990000) // 10000
    cleanDf[index] = df[index]
    dummyDf = []
    for i in range(1, codeRange+1):
        cleanDf['{}{}'.format(prcName, i)] = df['{}{}'.format(prcName, i)]
        currDummy = cleanDf[[index] + ['{}{}'.format(codeName, i)]]
        currDummy = pd.get_dummies(currDummy['{}{}'.format(codeName, i)], prefix = codeName)
        currDummy[index] = cleanDf[index]
        currDummy['{}{}'.format(prcName, i)] = cleanDf['{}{}'.format(prcName, i)]
        currDummy = pd.groupby(currDummy, index)[currDummy.columns].max()
        currDummy2 = currDummy.apply(lambda x: x[:-2] * x[-1], axis = 1)
        currDummy2[index] = currDummy[index]
        dummyDf.append(currDummy2)
    currDummy = dummyDf[0]
    for i in range(1, codeRange):
        currDummy = currDummy.add(dummyDf[i], fill_value = 0.)
        currDummy[index] = dummyDf[i][index]
        currDummy.fillna(0, inplace=True)
    return currDummy

def munge_data(df_orig):
    df = df_orig.copy()
    del df['Person.ID.1']
    # Find the oldest investigator's birth date
    oldest = pd.DataFrame(df.groupby('Grant.Application.ID')['Year.of.Birth.1'].min())
    
    
    # Get the number of investigators for each role
    numRole = pd.get_dummies(df['Role.1'])
    numRole['Grant.Application.ID'] = df['Grant.Application.ID']
    numRole = pd.groupby(numRole, 'Grant.Application.ID')[numRole.columns].sum()
    
    # Get the % of aussies
    numAussies = pd.get_dummies(df['Country.of.Birth.1'])
    numAussies['Grant.Application.ID'] = df['Grant.Application.ID']
    numAussies = pd.groupby(numAussies, 'Grant.Application.ID')[numAussies.columns].sum()
    
    # We just imputed all values with NaN (no country info) to zero
    prcAussies = pd.DataFrame((numAussies['Australia'] / numAussies.sum(axis = 1)).fillna(0), columns = ['% Australians'])
    
    # Sum the # of published papers
    
    numPapers = df.groupby('Grant.Application.ID')['A..1', 'A.1','B.1', 'C.1','Number.of.Successful.Grant.1','Number.of.Unsuccessful.Grant.1'].sum()
    numPapers = pd.DataFrame(numPapers) 

    
    df['Contract.Value.Band...see.note.A'].fillna('A', inplace=True)
    df['Contract.Value.Band...see.note.A']=df['Contract.Value.Band...see.note.A'].apply(lambda x: ord(x.rstrip(' ')))
    
    # converting categories to dummy variables
    
    grant_cats = pd.get_dummies(df['Grant.Category.Code'], dummy_na=True)    
    grant_cats['Grant.Application.ID']=df['Grant.Application.ID']
    grant_cats = pd.groupby(grant_cats, 'Grant.Application.ID')[grant_cats.columns].min()  
    grant_cats = pd.DataFrame(grant_cats)
    
    # imputing missing percentages for RFCD.Percentage columns with the mean
    df['RFCD.Percentage.1'].fillna(df['RFCD.Percentage.1'].mean(), inplace=True)
    df['RFCD.Percentage.2'].fillna(df['RFCD.Percentage.2'].mean(), inplace=True)
    df['RFCD.Percentage.3'].fillna(df['RFCD.Percentage.3'].mean(), inplace=True)
    df['RFCD.Percentage.4'].fillna(df['RFCD.Percentage.4'].mean(), inplace=True)
    df['RFCD.Percentage.5'].fillna(df['RFCD.Percentage.5'].mean(), inplace=True)
    
    # doing the same as above with SEO.Percentage columns
    df['SEO.Percentage.1'].fillna(df['SEO.Percentage.1'].mean(), inplace=True)
    df['SEO.Percentage.2'].fillna(df['SEO.Percentage.2'].mean(), inplace=True)
    df['SEO.Percentage.3'].fillna(df['SEO.Percentage.3'].mean(), inplace=True)
    df['SEO.Percentage.4'].fillna(df['SEO.Percentage.4'].mean(), inplace=True)
    df['SEO.Percentage.5'].fillna(df['SEO.Percentage.5'].mean(), inplace=True)
    rfcds = combine_columns(df, 'RFCD.Code.', 'RFCD.Percentage.')
    seos = combine_columns(df, 'SEO.Code.', 'SEO.Percentage.')
    
    # Get rid of everything we don't need
    # REMINDER - LATER COME BACK AND DEAL WITH DEPARTMENT, FACULTY, NO YEARS AT FACULTY, PHD, ETC
    df.drop(['A..1', u'A.1', u'B.1', u'C.1', u'Country.of.Birth.1', u'Dept.No..1', u'Faculty.No..1',
           u'Home.Language.1', u'No..of.Years.in.Uni.at.Time.of.Grant.1', u'Number.of.Successful.Grant.1',
           u'Number.of.Unsuccessful.Grant.1', u'Role.1', u'Sponsor.Code', u'With.PHD.1', u'Year.of.Birth.1',
           u'SEO.Code.4', u'SEO.Code.5', u'SEO.Code.1', u'SEO.Code.2', u'SEO.Code.3', u'RFCD.Code.1',
           u'RFCD.Code.2', u'RFCD.Code.3', u'RFCD.Code.4', u'RFCD.Code.5', 'Grant.Category.Code', u'RFCD.Percentage.1', u'RFCD.Percentage.2', u'RFCD.Percentage.3', u'RFCD.Percentage.4', u'RFCD.Percentage.5', u'SEO.Percentage.1', u'SEO.Percentage.2', u'SEO.Percentage.3', u'SEO.Percentage.4', u'SEO.Percentage.5',], inplace = True, axis = 1)
    df.drop_duplicates(inplace = True)
    df.set_index('Grant.Application.ID', inplace=True)
    
    finalDf = pd.merge(df, oldest, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, numRole, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, prcAussies, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, numPapers, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, grant_cats, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, rfcds, left_index = True, right_index = True)
    finalDf = pd.merge(finalDf, seos, left_index = True, right_index = True)
    
    #imputing ages with median
    finalDf['Year.of.Birth.1'].fillna(finalDf['Year.of.Birth.1'].median(), inplace = True)
    
    #imputing missing papers with 0
    finalDf['A..1'].fillna(0, inplace = True)
    finalDf['A.1'].fillna(0, inplace = True)
    finalDf['B.1'].fillna(0, inplace = True)
    finalDf['C.1'].fillna(0, inplace = True)
    
    #imputing missing successful and unsuccessful grants with 0
    finalDf['Number.of.Successful.Grant.1'].fillna(0, inplace = True)
    finalDf['Number.of.Unsuccessful.Grant.1'].fillna(0, inplace = True)
        
    del finalDf['Grant.Application.ID_y']
    del finalDf['Grant.Application.ID_x']
    finalDf['Proc.Start.Date'] = finalDf['Start.date'].apply(lambda x:
                          time.mktime(datetime.datetime.strptime(x,'%d/%m/%y').timetuple()))
   #splitting dataframe
    mask = time_mask(finalDf)
    finalDf_test = finalDf[mask]
    finalDf_train = finalDf[-mask]
    
    #creating X, y splits for test and train dataframes
    y_train = finalDf_train['Grant.Status'].values
    del finalDf_train['Grant.Status']
    del finalDf_train['Start.date']
    X_train = finalDf_train.values
    
    y_test = finalDf_test['Grant.Status'].values
    del finalDf_test['Grant.Status']
    del finalDf_test['Start.date']
    X_test = finalDf_test.values
	
    return X_train, y_train, X_test, y_test, finalDf_test, finalDf_train

def time_mask(df, key = 'Proc.Start.Date', value = '01/01/08'):
	t = time.mktime( datetime.datetime.strptime(value,'%d/%m/%y').timetuple())
	return df[key] >= t

def testing(X, y):
	estimators = [
		('scale_predictors', StandardScaler()),
		('feature_selector', LinearSVC(penalty='l1', dual=False)),
		#('feature_selector', SelectKBest(score_func=f_classif)),
		('linearSVC', LinearSVC())
		#('randomforests', RandomForestClassifier())
		]
	clf = Pipeline(estimators)
	params = dict(
		linearSVC__C=[0.1, 1, 10],
		#randomforests__max_depth=[5, 10, None], 
		#randomforests__n_estimators=[10, 50, 100], 
		feature_selector__C=[0.1, 1, 10]
		#feature_selector__score_func=[chi2],
		#feature_selector__k=[5, 10, 'all'] 
		)
	grid_search = GridSearchCV(clf, param_grid=params)
	grid_search.fit(X, y)
	return grid_search

def performance(results, param1, param2):
	param1_vals = [x.parameters[param1] for x in results.grid_scores_]
	param2_vals = [x.parameters[param2] for x in results.grid_scores_]
	means = [x.mean_validation_score for x in results.grid_scores_]
	df = pd.DataFrame(zip(param1_vals, param2_vals, means), columns = [param1, param2, 'means'])
	df.fillna('None', inplace=True)
	return pd.pivot_table(df, values = 'means' , index = param1, columns = param2)
