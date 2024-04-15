def SofiaUniversity_tuition(df):
    df.columns = ['Degree', 'Degree Program', 'Total Units', 'Estimated Tuition', 'Estimated Fees']
    df.Degree = df.Degree.fillna(method='ffill')
    df = df.dropna(thresh=3)
    df = df.drop(0)
    df = df.reset_index(drop=True)
    return df
