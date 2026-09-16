import pandas as pd


def detect_market_regime(df):

    recent = df.tail(30)

    highest = recent["high"].max()
    lowest = recent["low"].min()

    price_range = highest - lowest

    avg_close = recent["close"].mean()

    volatility = price_range / avg_close

    if volatility > 0.08:
        return "High Volatility"

    elif volatility < 0.015:
        return "Low Volatility"

    else:
        return "Normal"
