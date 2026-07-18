"""
BLISSFINITY SIGNAL BOT
MARKET REGIME ENGINE
"""

import pandas as pd


def detect_market_regime(df: pd.DataFrame):

    df = df.copy()

    # EMA
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    # ATR
    df["tr"] = df["high"] - df["low"]
    atr = df["tr"].rolling(14).mean().iloc[-1]

    # Average candle range
    avg_range = df["tr"].rolling(20).mean().iloc[-1]

    ema_distance = abs(
        df["ema50"].iloc[-1] -
        df["ema200"].iloc[-1]
    )

    # Trending
    if ema_distance > atr * 1.5:
        return {
            "regime": "TRENDING",
            "quality": 90
        }

    # Breakout
    if df["close"].iloc[-1] > df["high"].rolling(20).max().iloc[-2]:
        return {
            "regime": "BREAKOUT",
            "quality": 95
        }

    # High Volatility
    if atr > avg_range * 1.5:
        return {
            "regime": "HIGH_VOLATILITY",
            "quality": 70
        }

    # Low Volatility
    if atr < avg_range * 0.6:
        return {
            "regime": "LOW_VOLATILITY",
            "quality": 30
        }

    return {
        "regime": "RANGING",
        "quality": 50
    }