"""
BLISSFINITY AI SIGNAL BOT
4H Break of Structure Engine
"""


def bullish_bos(df):
    """
    Bullish BOS:
    Latest close breaks above previous swing high.
    """

    if len(df) < 5:
        return False

    previous_high = max(df.iloc[-5:-1]["high"])
    current_close = df.iloc[-1]["close"]

    return current_close > previous_high


def bearish_bos(df):
    """
    Bearish BOS:
    Latest close breaks below previous swing low.
    """

    if len(df) < 5:
        return False

    previous_low = min(df.iloc[-5:-1]["low"])
    current_close = df.iloc[-1]["close"]

    return current_close < previous_low