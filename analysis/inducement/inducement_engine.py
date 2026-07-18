"""
BLISSFINITY AI SIGNAL BOT
INDUCEMENT ENGINE
"""

import pandas as pd


def detect_inducement(df: pd.DataFrame):
    """
    Detect potential inducement before
    institutional movement.
    """

    if len(df) < 30:

        return {

            "inducement": False,

            "direction": None,

            "level": None,

            "reason": "Not enough candles"

        }

    recent = df.tail(20)

    equal_high = recent["high"].value_counts().max() >= 2
    equal_low = recent["low"].value_counts().max() >= 2

    last = recent.iloc[-1]

    # BUY inducement
    if equal_low and last["low"] < recent["low"].min():

        return {

            "inducement": True,

            "direction": "BUY",

            "level": float(last["low"]),

            "reason": "Liquidity taken below equal lows"

        }

    # SELL inducement
    if equal_high and last["high"] > recent["high"].max():

        return {

            "inducement": True,

            "direction": "SELL",

            "level": float(last["high"]),

            "reason": "Liquidity taken above equal highs"

        }

    return {

        "inducement": False,

        "direction": None,

        "level": None,

        "reason": "No inducement"

    }