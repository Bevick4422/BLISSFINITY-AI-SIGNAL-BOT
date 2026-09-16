"""
BLISSFINITY AI SIGNAL BOT
INSTITUTIONAL LIQUIDITY ENGINE
"""

import pandas as pd


def detect_institutional_liquidity(df: pd.DataFrame):
    """
    Detect institutional liquidity pools.
    """

    highs = df["high"]
    lows = df["low"]

    tolerance = 0.0015

    equal_highs = []
    equal_lows = []

    # ---------------------------------
    # Equal Highs
    # ---------------------------------

    for i in range(len(df)-15, len(df)-1):

        for j in range(i+1, len(df)):

            if abs(highs.iloc[i]-highs.iloc[j]) <= highs.iloc[i]*tolerance:

                equal_highs.append(float(highs.iloc[i]))

    # ---------------------------------
    # Equal Lows
    # ---------------------------------

    for i in range(len(df)-15, len(df)-1):

        for j in range(i+1, len(df)):

            if abs(lows.iloc[i]-lows.iloc[j]) <= lows.iloc[i]*tolerance:

                equal_lows.append(float(lows.iloc[i]))

    latest_high = float(highs.iloc[-1])
    latest_low = float(lows.iloc[-1])

    buy_side_sweep = False
    sell_side_sweep = False

    # ---------------------------------
    # Buy-side sweep
    # ---------------------------------

    for level in equal_highs:

        if latest_high > level:

            buy_side_sweep = True
            break

    # ---------------------------------
    # Sell-side sweep
    # ---------------------------------

    for level in equal_lows:

        if latest_low < level:

            sell_side_sweep = True
            break

    return {

        "equal_highs": equal_highs,

        "equal_lows": equal_lows,

        "buy_side_sweep": buy_side_sweep,

        "sell_side_sweep": sell_side_sweep,

        "liquidity_grab": (
            buy_side_sweep
            or
            sell_side_sweep
        )

    }