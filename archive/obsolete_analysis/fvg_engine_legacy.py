
"""
BLISSFINITY AI SIGNAL BOT
FAIR VALUE GAP ENGINE
"""

import pandas as pd


def detect_fvg(df: pd.DataFrame):
    """
    Detect bullish and bearish Fair Value Gaps.
    """

    if len(df) < 3:
        return {
            "bullish_fvg": False,
            "bearish_fvg": False,
            "bullish_zone": None,
            "bearish_zone": None
        }

    c1 = df.iloc[-3]
    c2 = df.iloc[-2]
    c3 = df.iloc[-1]

    bullish = c1["high"] < c3["low"]

    bearish = c1["low"] > c3["high"]

    bullish_zone = None
    bearish_zone = None

    if bullish:
        bullish_zone = (
            round(c1["high"], 4),
            round(c3["low"], 4)
        )

    if bearish:
        bearish_zone = (
            round(c3["high"], 4),
            round(c1["low"], 4)
        )

    return {

        "bullish_fvg": bullish,

        "bearish_fvg": bearish,

        "bullish_zone": bullish_zone,

        "bearish_zone": bearish_zone

    }