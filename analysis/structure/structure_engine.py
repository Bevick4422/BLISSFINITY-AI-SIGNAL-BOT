
"""
BLISSFINITY AI SIGNAL BOT
MARKET STRUCTURE ENGINE
"""

import pandas as pd


def detect_structure(df: pd.DataFrame):
    """
    Detect market structure using swing highs/lows.
    """

    highs = df["high"]
    lows = df["low"]

    recent_high = highs.iloc[-1]
    previous_high = highs.iloc[-5:-1].max()

    recent_low = lows.iloc[-1]
    previous_low = lows.iloc[-5:-1].min()

    bos = False
    choch = False

    structure = "RANGE"

    # =============================
    # Bullish Structure
    # =============================

    if recent_high > previous_high:

        structure = "BULLISH"

        bos = True

    # =============================
    # Bearish Structure
    # =============================

    elif recent_low < previous_low:

        structure = "BEARISH"

        bos = True

    # =============================
    # Change of Character
    # =============================

    if (
        recent_high < previous_high
        and recent_low > previous_low
    ):

        choch = True

    return {

        "trend_structure": structure,

        "bos": bos,

        "choch": choch,

        "recent_high": float(recent_high),

        "previous_high": float(previous_high),

        "recent_low": float(recent_low),

        "previous_low": float(previous_low)

    }