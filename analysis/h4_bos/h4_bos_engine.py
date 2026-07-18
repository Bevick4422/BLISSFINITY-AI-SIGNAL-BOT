"""
BLISSFINITY AI SIGNAL BOT
INSTITUTIONAL 4H BOS ENGINE
"""

import pandas as pd


def detect_h4_bos(df: pd.DataFrame):
    """
    Detect institutional Break of Structure (BOS)
    using confirmed swing highs/lows.

    Rules:
    - Body close required
    - Swing must be broken
    """

    lookback = 5

    highs = df["high"]
    lows = df["low"]
    closes = df["close"]

    swing_high = None
    swing_low = None

    # =====================================
    # Find latest swing high
    # =====================================

    for i in range(len(df) - lookback - 2, lookback, -1):

        if highs.iloc[i] == max(highs.iloc[i-lookback:i+lookback+1]):

            swing_high = float(highs.iloc[i])

            break

    # =====================================
    # Find latest swing low
    # =====================================

    for i in range(len(df) - lookback - 2, lookback, -1):

        if lows.iloc[i] == min(lows.iloc[i-lookback:i+lookback+1]):

            swing_low = float(lows.iloc[i])

            break

    current_close = float(closes.iloc[-1])

    bos = False
    direction = None
    broken_level = None

    # =====================================
    # Bullish BOS
    # =====================================

    if swing_high is not None:

        if current_close > swing_high:

            bos = True
            direction = "BUY"
            broken_level = swing_high

    # =====================================
    # Bearish BOS
    # =====================================

    if (not bos) and (swing_low is not None):

        if current_close < swing_low:

            bos = True
            direction = "SELL"
            broken_level = swing_low

    return {

        "bos": bos,

        "direction": direction,

        "broken_level": broken_level,

        "swing_high": swing_high,

        "swing_low": swing_low

    }