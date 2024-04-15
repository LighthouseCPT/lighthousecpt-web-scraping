import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def SofiaUniversity_requirement(df):
    df.columns = ('MBA Admission Requirements', 'Required For')
    df['Required For'] = 'Everyone'
    qqq = df.loc[df['MBA Admission Requirements'] == 'F-1 Admissions Requirements'].index[0]
    df.loc[df.index > qqq, 'Required For'] = 'F-1 Admissions'
    df = df.drop(7)
    df = df.reset_index(drop=True)
    return df
