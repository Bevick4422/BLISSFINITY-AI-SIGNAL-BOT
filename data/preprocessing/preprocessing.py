import pandas as pd


def preprocess(df):

    df = df.copy()

    # Remove duplicate candles
    df = df.drop_duplicates()

    # Remove missing values
    df = df.dropna()

    # Reset index
    df.reset_index(drop=True, inplace=True)

    return df
