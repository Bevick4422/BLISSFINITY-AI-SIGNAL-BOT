"""
BLISSFINITY Order Block Engine
"""

import pandas as pd


def detect_order_block(df: pd.DataFrame):

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

    elif last["close"] < last["open"]:
        return {
            "type": "BEARISH",
            "strength": 100
        }

    return {
        "type": None,
        "strength": 0
    }
