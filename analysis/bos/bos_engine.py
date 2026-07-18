"""
BLISSFINITY AI SIGNAL BOT
4H BREAK OF STRUCTURE ENGINE
"""

import pandas as pd


def detect_bos(df: pd.DataFrame):
    """
    Detect a valid Break of Structure (BOS)
    using full candle body closes.
    """

    if len(df) < 30:
        return {
            "bos": False,
            "direction": None,
            "level": None,
            "reason": "Not enough candles"
        }

    # Previous swing levels
    swing_high = df["high"].iloc[-21:-1].max()
    swing_low = df["low"].iloc[-21:-1].min()

    last = df.iloc[-1]

    body_high = max(last["open"], last["close"])
    body_low = min(last["open"], last["close"])

    # -------------------------
    # Bullish BOS
    # -------------------------

    if body_low > swing_high:

        return {

            "bos": True,

            "direction": "BUY",

            "level": float(swing_high),

            "reason": "Bullish BOS"

        }

    # -------------------------
    # Bearish BOS
    # -------------------------

    if body_high < swing_low:

        return {

            "bos": True,

            "direction": "SELL",

            "level": float(swing_low),

            "reason": "Bearish BOS"

        }

    return {

        "bos": False,

        "direction": None,

        "level": None,

        "reason": "No BOS"

    }