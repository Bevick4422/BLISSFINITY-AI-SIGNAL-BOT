"""
BLISSFINITY Order Block Engine
"""

import pandas as pd


def detect_order_block(df: pd.DataFrame):
    """
    Detect the latest order block.

    Returns:
    {
        "type": "BULLISH" | "BEARISH" | None,
        "strength": int
    }
    """

    if len(df) < 10:
        return {
            "type": None,
            "strength": 0
        }

    last = df.iloc[-1]

    if last["close"] > last["open"]:
        return {
            "type": "BULLISH",
            "strength": 100
        }

    if last["close"] < last["open"]:
        return {
            "type": "BEARISH",
            "strength": 100
        }

    return {
        "type": None,
        "strength": 0
    }
