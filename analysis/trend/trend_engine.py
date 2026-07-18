
"""
BLISSFINITY AI SIGNAL BOT
TREND ENGINE
"""

import pandas as pd


def detect_trend(df: pd.DataFrame):
    """
    Detects the higher timeframe trend using EMA 50 and EMA 200.
    """

    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    price = df["close"].iloc[-1]

    if ema50 > ema200 and price > ema50:
        trend = "BULLISH"

    elif ema50 < ema200 and price < ema50:
        trend = "BEARISH"

    else:
        trend = "RANGING"

    return {
        "trend": trend,
        "ema50": round(ema50, 2),
        "ema200": round(ema200, 2),
        "price": round(price, 2)
    }