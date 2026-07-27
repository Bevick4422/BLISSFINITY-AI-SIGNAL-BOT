"""
BLISSFINITY AI SIGNAL BOT
Bullish / Bearish Engulfing Detection
"""


def bullish_engulfing(df):
    """
    Returns True if the latest daily candle is a bullish engulfing candle.
    """

    if len(df) < 2:
        return False

    previous = df.iloc[-2]
    current = df.iloc[-1]

    return (
        previous["close"] < previous["open"]
        and current["close"] > current["open"]
        and current["open"] <= previous["close"]
        and current["close"] >= previous["open"]
    )


def bearish_engulfing(df):
    """
    Returns True if the latest daily candle is a bearish engulfing candle.
    """

    if len(df) < 2:
        return False

    previous = df.iloc[-2]
    current = df.iloc[-1]

    return (
        previous["close"] > previous["open"]
        and current["close"] < current["open"]
        and current["open"] >= previous["close"]
        and current["close"] <= previous["open"]
    )