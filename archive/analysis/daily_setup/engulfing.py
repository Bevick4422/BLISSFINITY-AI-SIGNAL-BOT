"""
BLISSFINITY SIGNAL
Daily Engulfing Detection
"""

from __future__ import annotations


# ============================================================
# BULLISH ENGULFING
# ============================================================

def bullish_engulfing(df) -> bool:
    """
    Confirm a bullish engulfing pattern.

    The latest candle must be bullish and completely
    engulf the previous bearish candle.
    """

    if df is None or len(df) < 2:
        return False

    previous = df.iloc[-2]
    current = df.iloc[-1]

    return (
        previous["close"] < previous["open"]
        and current["close"] > current["open"]
        and current["open"] <= previous["close"]
        and current["close"] >= previous["open"]
    )


# ============================================================
# BEARISH ENGULFING
# ============================================================

def bearish_engulfing(df) -> bool:
    """
    Confirm a bearish engulfing pattern.

    The latest candle must be bearish and completely
    engulf the previous bullish candle.
    """

    if df is None or len(df) < 2:
        return False

    previous = df.iloc[-2]
    current = df.iloc[-1]

    return (
        previous["close"] > previous["open"]
        and current["close"] < current["open"]
        and current["open"] >= previous["close"]
        and current["close"] <= previous["open"]
    )


# ============================================================
# ENGULFING SETUP
# ============================================================

def detect_engulfing(df):
    """
    Return the confirmed Daily engulfing setup.

    Returns:

        {
            "direction": "BUY" | "SELL",
            "setup": "Bullish Engulfing" |
                     "Bearish Engulfing",
            "entry": float,
            "valid": True
        }

    or:

        None
    """

    if df is None or len(df) < 2:
        return None

    current = df.iloc[-1]

    # --------------------------------------------------------
    # BULLISH
    # --------------------------------------------------------

    if bullish_engulfing(df):

        return {
            "direction": "BUY",
            "setup": "Bullish Engulfing",
            "entry": float(current["close"]),
            "valid": True,
        }

    # --------------------------------------------------------
    # BEARISH
    # --------------------------------------------------------

    if bearish_engulfing(df):

        return {
            "direction": "SELL",
            "setup": "Bearish Engulfing",
            "entry": float(current["close"]),
            "valid": True,
        }

    return None