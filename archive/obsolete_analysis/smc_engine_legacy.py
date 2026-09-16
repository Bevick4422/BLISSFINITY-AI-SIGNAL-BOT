"""
BLISSFINITY AI SIGNAL BOT
SMART MONEY CONCEPT ENGINE
"""

import pandas as pd


def detect_smc(df: pd.DataFrame):

    if len(df) < 30:
        return {
            "bullish_order_block": False,
            "bearish_order_block": False,
            "bullish_fvg": False,
            "bearish_fvg": False,
        }

    bullish_ob = (
        df["close"].iloc[-2] < df["open"].iloc[-2]
        and df["close"].iloc[-1] > df["high"].iloc[-2]
    )

    bearish_ob = (
        df["close"].iloc[-2] > df["open"].iloc[-2]
        and df["close"].iloc[-1] < df["low"].iloc[-2]
    )

    bullish_fvg = (
        df["low"].iloc[-1] >
        df["high"].iloc[-3]
    )

    bearish_fvg = (
        df["high"].iloc[-1] <
        df["low"].iloc[-3]
    )

    return {

        "bullish_order_block": bullish_ob,
        "bearish_order_block": bearish_ob,
        "bullish_fvg": bullish_fvg,
        "bearish_fvg": bearish_fvg,

    }