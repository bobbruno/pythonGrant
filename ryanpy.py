# Ryan's code

import pandas as pd

def get_tables(filename = 'raw.csv'):
    df_raw = pd.read_csv(filename)
    del df_raw['Unnamed: 0']
    df_grants = df_raw[df_raw.columns[:26]]
    investigator_columns = [df_raw[df_raw.columns[0:26] + df_raw.columns[26 + 15*i : 26 + 15 * (i+1)]] for i in range(len(df_raw.columns[26:])/15)]
    for table in investigator_columns:
        table.columns = df_raw.columns[0:26] + investigator_columns[0].columns
    investigators = pd.concat(investigator_columns)
    unique_investigators = investigators.drop_duplicates()
    return unique_investigators[unique_investigators['Role.1'].isnull()==False].sort('Grant.Application.ID')