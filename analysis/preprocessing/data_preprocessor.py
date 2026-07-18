"""
BLISSFINITY SIGNAL BOT
DATA PREPROCESSING ENGINE
"""

import pandas as pd


def preprocess(df: pd.DataFrame):

    df = df.copy()

    # -------------------
    # Candle Features
    # -------------------

    df["body"] = abs(df["close"] - df["open"])

    df["range"] = df["high"] - df["low"]

    df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)

    df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]

    # -------------------
    # ATR
    # -------------------

    tr = pd.concat([
        df["high"] - df["low"],
        abs(df["high"] - df["close"].shift()),
        abs(df["low"] - df["close"].shift())
    ], axis=1).max(axis=1)

    df["ATR"] = tr.rolling(14).mean()

    # -------------------
    # EMA
    # -------------------

    df["EMA20"] = df["close"].ewm(span=20).mean()

    df["EMA50"] = df["close"].ewm(span=50).mean()

    df["EMA200"] = df["close"].ewm(span=200).mean()

    # -------------------
    # Volume
    # -------------------

    df["avg_volume"] = df["volume"].rolling(20).mean()

    df["volume_ratio"] = (
        df["volume"] /
        df["avg_volume"]
    )

    return df