import pandas as pd


def validate_data(df: pd.DataFrame):

    df = df.copy()

    df = df.dropna()

    df = df.drop_duplicates()

    df = df.sort_values("timestamp")

    df = df.reset_index(drop=True)

    return df
