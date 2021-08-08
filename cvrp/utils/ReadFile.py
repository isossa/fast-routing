import pandas as pd


def read_csv(filename: str, header=None) -> list:
    data = pd.read_csv(filename, header=header)
    return data.values.tolist()
