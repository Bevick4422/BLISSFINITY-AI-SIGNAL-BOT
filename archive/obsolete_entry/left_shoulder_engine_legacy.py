"""
BLISSFINITY AI SIGNAL BOT
LEFT SHOULDER / INVERSE LEFT SHOULDER ENGINE
"""

import pandas as pd


def detect_left_shoulder(df: pd.DataFrame):
    """
    Detect Left Shoulder and Inverse Left Shoulder.
    """

    if len(df) < 40:

        return {

            "pattern": None,

            "confirmed": False,

            "reason": "Not enough candles"

        }

    highs = df["high"].tail(20).tolist()
    lows = df["low"].tail(20).tolist()

    last_high = max(highs[:-1])
    current_high = highs[-1]

    last_low = min(lows[:-1])
    current_low = lows[-1]

    # ==================================
    # Inverse Left Shoulder (BUY)
    # ==================================

    if current_low > last_low:

        return {

            "pattern": "INVERSE_LEFT_SHOULDER",

            "direction": "BUY",

            "confirmed": True,

            "level": float(current_low)

        }

    # ==================================
    # Left Shoulder (SELL)
    # ==================================

    if current_high < last_high:

        return {

            "pattern": "LEFT_SHOULDER",

            "direction": "SELL",

            "confirmed": True,

            "level": float(current_high)

        }

    return {

        "pattern": None,

        "direction": None,

        "confirmed": False,

        "level": None

    }