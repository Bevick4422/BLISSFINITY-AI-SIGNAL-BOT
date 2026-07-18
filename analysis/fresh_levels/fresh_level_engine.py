"""
BLISSFINITY AI SIGNAL BOT
FRESH LEVEL ENGINE
"""

import pandas as pd


def is_level_fresh(df: pd.DataFrame, level: dict):
    """
    Check whether an A/V level has been mitigated.
    """

    if level is None:
        return False

    price = level["price"]
    index = level["index"]

    future = df.iloc[index + 1:]

    if level["type"] == "V":

        # Demand level is mitigated if price trades back below it
        touched = future["low"] <= price

    else:

        # Supply level is mitigated if price trades back above it
        touched = future["high"] >= price

    return not touched.any()


def detect_fresh_levels(df: pd.DataFrame, key_levels: dict):
    """
    Return only fresh institutional levels.
    """

    latest_v = key_levels["latest_v"]
    latest_a = key_levels["latest_a"]

    fresh_v = (
        latest_v
        if is_level_fresh(df, latest_v)
        else None
    )

    fresh_a = (
        latest_a
        if is_level_fresh(df, latest_a)
        else None
    )

    return {

        "fresh_v": fresh_v,

        "fresh_a": fresh_a,

        "has_fresh_level": (
            fresh_v is not None
            or fresh_a is not None
        )

    }