
"""
BLISSFINITY AI SIGNAL BOT
Fresh Level Detection
"""

LOOKBACK = 20


def is_fresh_support(df, level):
    """
    Returns True if support has never been broken
    after the support was created.
    """

    if level is None:
        return False

    candles = df.tail(LOOKBACK).iloc[1:]

    return (candles["low"] >= level).all()


def is_fresh_resistance(df, level):
    """
    Returns True if resistance has never been broken
    after the resistance was created.
    """

    if level is None:
        return False

    candles = df.tail(LOOKBACK).iloc[1:]

    return (candles["high"] <= level).all()