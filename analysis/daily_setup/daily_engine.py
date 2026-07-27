"""
BLISSFINITY AI SIGNAL BOT
Daily Setup Engine
"""

from analysis.daily_setup.engulfing import (
    bullish_engulfing,
    bearish_engulfing,
)

from analysis.daily_setup.keylevels import (
    find_v_shape,
    find_a_shape,
)

from analysis.daily_setup.fresh_levels import (
    is_fresh_support,
    is_fresh_resistance,
)

# Enable/Disable console debugging
DEBUG = True


def detect_daily_setup(df):
    """
    Detect the highest-priority daily setup.

    Priority:
        1. Bullish Engulfing
        2. Bearish Engulfing
        3. Fresh V Shape
        4. Fresh A Shape

    Returns:
        {
            "direction": "BUY" | "SELL" | None,
            "setup": str,
            "level": float | None,
            "valid": bool,
        }
    """

    # --------------------------------------------------
    # Detect Patterns
    # --------------------------------------------------

    bullish = bullish_engulfing(df)
    bearish = bearish_engulfing(df)

    v_level = find_v_shape(df)
    a_level = find_a_shape(df)

    fresh_support = (
        is_fresh_support(df, v_level)
        if v_level is not None
        else False
    )

    fresh_resistance = (
        is_fresh_resistance(df, a_level)
        if a_level is not None
        else False
    )

    # --------------------------------------------------
    # Debug
    # --------------------------------------------------

    if DEBUG:
        print("\n" + "=" * 60)
        print("DAILY SETUP DEBUG")
        print("=" * 60)
        print(f"Bullish Engulfing : {bullish}")
        print(f"Bearish Engulfing : {bearish}")
        print(f"V Shape Level     : {v_level}")
        print(f"A Shape Level     : {a_level}")
        print(f"Fresh Support     : {fresh_support}")
        print(f"Fresh Resistance  : {fresh_resistance}")
        print("=" * 60)

    # --------------------------------------------------
    # 1. Bullish Engulfing
    # Immediate BUY signal
    # --------------------------------------------------

    if bullish:
        return {
            "direction": "BUY",
            "setup": "Bullish Engulfing",
            "level": v_level,
            "valid": True,
        }

    # --------------------------------------------------
    # 2. Bearish Engulfing
    # Immediate SELL signal
    # --------------------------------------------------

    if bearish:
        return {
            "direction": "SELL",
            "setup": "Bearish Engulfing",
            "level": a_level,
            "valid": True,
        }

    # --------------------------------------------------
    # 3. Fresh V Shape
    # Wait for H4 BOS
    # --------------------------------------------------

    if fresh_support:
        return {
            "direction": "BUY",
            "setup": "V Shape",
            "level": v_level,
            "valid": True,
        }

    # --------------------------------------------------
    # 4. Fresh A Shape
    # Wait for H4 BOS
    # --------------------------------------------------

    if fresh_resistance:
        return {
            "direction": "SELL",
            "setup": "A Shape",
            "level": a_level,
            "valid": True,
        }

    # --------------------------------------------------
    # No Valid Setup
    # --------------------------------------------------

    return {
        "direction": None,
        "setup": "NONE",
        "level": None,
        "valid": False,
    }