"""
BLISSFINITY AI SIGNAL BOT
A-SHAPE / V-SHAPE KEY LEVEL ENGINE
"""

import pandas as pd


def detect_key_levels(df: pd.DataFrame):
    """
    Detect institutional A-Shape and V-Shape levels.
    """

    levels = []

    for i in range(1, len(df) - 1):

        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        nxt = df.iloc[i + 1]

        # ==================================
        # V SHAPE (Support)
        # Bear Candle -> Bull Candle
        # ==================================

        if (
            prev["close"] < prev["open"]
            and curr["close"] > curr["open"]
        ):

            levels.append({

                "type": "V",

                "price": float(min(prev["low"], curr["low"])),

                "index": i

            })

        # ==================================
        # A SHAPE (Resistance)
        # Bull Candle -> Bear Candle
        # ==================================

        if (
            prev["close"] > prev["open"]
            and curr["close"] < curr["open"]
        ):

            levels.append({

                "type": "A",

                "price": float(max(prev["high"], curr["high"])),

                "index": i

            })

    latest_v = None
    latest_a = None

    for level in reversed(levels):

        if latest_v is None and level["type"] == "V":
            latest_v = level

        if latest_a is None and level["type"] == "A":
            latest_a = level

        if latest_v and latest_a:
            break

    return {

        "latest_v": latest_v,

        "latest_a": latest_a,

        "all_levels": levels

    }