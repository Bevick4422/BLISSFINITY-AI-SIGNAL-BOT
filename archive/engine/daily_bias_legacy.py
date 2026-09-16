
"""
BLISSFINITY AI SIGNAL BOT
Daily Bias Engine
"""

import pandas as pd


def get_daily_bias(df: pd.DataFrame):
    """
    Determine the higher timeframe trend.

    Returns:
        BUY
        SELL
        NEUTRAL
    """

    if len(df) < 20:
        return "NEUTRAL"

    close = df["close"]

    ema20 = close.ewm(span=20).mean()

    current_close = close.iloc[-1]
    current_ema = ema20.iloc[-1]

    last5 = close.tail(5)

    higher_high = last5.max() == current_close
    lower_low = last5.min() == current_close

    # -----------------------------
    # Bullish Trend
    # -----------------------------

    if current_close > current_ema and higher_high:
        return "BUY"

    # -----------------------------
    # Bearish Trend
    # -----------------------------

    if current_close < current_ema and lower_low:
        return "SELL"

    return "NEUTRAL"