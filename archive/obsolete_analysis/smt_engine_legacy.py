import pandas as pd


def detect_smt_divergence(df1: pd.DataFrame,
                          df2: pd.DataFrame):

    if len(df1) < 5 or len(df2) < 5:
        return {
            "type": None
        }

    high1 = df1["high"].iloc[-1]
    prev_high1 = df1["high"].iloc[-2]

    high2 = df2["high"].iloc[-1]
    prev_high2 = df2["high"].iloc[-2]

    low1 = df1["low"].iloc[-1]
    prev_low1 = df1["low"].iloc[-2]

    low2 = df2["low"].iloc[-1]
    prev_low2 = df2["low"].iloc[-2]

    if high1 > prev_high1 and high2 <= prev_high2:
        return {
            "type": "BEARISH"
        }

    if low1 < prev_low1 and low2 >= prev_low2:
        return {
            "type": "BULLISH"
        }

    return {
        "type": None
    }
