def MonroeCollege_tuition(df):
    df.columns = range(df.shape[1])
    df.drop(df.columns[4], axis=1, inplace=True)
    df[1] = df[1].apply(lambda x: x + ' and Fees' if str(x) == 'Full time Tuition' else x)
    df[2] = df[2].apply(lambda x: x + ' Credit' if str(x) == 'Cost Per' else x)
    df.loc[df[1] == 'Full time Tuition and Fees', 2] = 'Cost Per Credit'
    df[3] = df[3].apply(lambda x: x + ' Class' if str(x) == 'Cost Per' else x)
    df[2] = df[2].combine_first(df[3])
    df.drop(df.columns[3], axis=1, inplace=True)
    df = df.loc[~df[0].isin(["and Fees", "Credit", "Class"])]

    return df
