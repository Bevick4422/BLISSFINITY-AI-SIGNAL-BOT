"""
BLISSFINITY AI SIGNAL BOT
Rejection Detection Engine
"""


def bullish_rejection(candle, support):
    """
    Bullish rejection of a support level.
    """

    return (
        candle["low"] <= support
        and candle["close"] > support
        and candle["close"] > candle["open"]
    )


def bearish_rejection(candle, resistance):
    """
    Bearish rejection of a resistance level.
    """

    return (
        candle["high"] >= resistance
        and candle["close"] < resistance
        and candle["close"] < candle["open"]
    )