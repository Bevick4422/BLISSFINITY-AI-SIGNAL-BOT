"""
BLISSFINITY AI SIGNAL BOT
DAILY CONFIRMATION ENGINE
"""

import pandas as pd


def detect_daily_confirmation(
    weekly_bias: dict,
    daily_df: pd.DataFrame
):
    """
    Confirm that Daily price action agrees
    with the Weekly Bias.
    """

    if len(daily_df) < 3:

        return {

            "confirmed": False,

            "reason": "Not enough daily candles"

        }

    last = daily_df.iloc[-1]

    previous = daily_df.iloc[-2]

    # ===============================
    # BUY Confirmation
    # ===============================

    if weekly_bias["bias"] == "BUY":

        if (

            last["close"] > previous["high"]

        ):

            return {

                "confirmed": True,

                "direction": "BUY",

                "reason": "Daily Bullish Break"

            }

    # ===============================
    # SELL Confirmation
    # ===============================

    if weekly_bias["bias"] == "SELL":

        if (

            last["close"] < previous["low"]

        ):

            return {

                "confirmed": True,

                "direction": "SELL",

                "reason": "Daily Bearish Break"

            }

    return {

        "confirmed": False,

        "reason": "Daily confirmation missing"

    }