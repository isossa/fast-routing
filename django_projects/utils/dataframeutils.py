import pandas as pd


def standardize_dataframe_columns(dataframe: pd.DataFrame, inplace=True):
    if inplace:
        dataframe.columns = ['_'.join(c.split(' ')) for c in dataframe.columns]
        return dataframe
    else:
        data = dataframe
        data.columns = ['_'.join(c.split(' ')) for c in dataframe.columns]
        return data
