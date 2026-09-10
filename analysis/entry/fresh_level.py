"""
BLISSFINITY SIGNAL
Fresh H4 Level Detection

A level is considered FRESH only when:

1. The level has a known creation candle.
2. Price moves away from the level after creation.
3. No later H4 candle touches the level.
4. A wick touching the level counts as mitigation.
5. A body touching the level counts as mitigation.
6. An exact price touch counts as mitigation.

The creation candle itself is ignored when checking mitigation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


MIN_REQUIRED_CANDLES = 3
DEFAULT_CONFIDENCE = 85


# ==========================================================
# RESULT HELPERS
# ==========================================================

def invalid_result(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": None,
        "entry": None,
        "confidence": 0,
        "reason": reason,
    }


# ==========================================================
# LEVEL TOUCH
# ==========================================================

def candle_touches_level(
    candle,
    level: float,
) -> bool:
    """
    Return True if the candle wick or body touches the level.

    Any price overlap with the level means the level has
    been mitigated.
    """

    try:
        low = float(candle["low"])
        high = float(candle["high"])

    except (KeyError, TypeError, ValueError):
        return True

    return low <= level <= high


# ==========================================================
# PRICE MOVED AWAY
# ==========================================================

def price_moved_away(
    candle,
    level: float,
    direction: str,
) -> bool:
    """
    Confirm that price has moved away from the level.

    BUY / demand:
        Candle must trade above the level.

    SELL / supply:
        Candle must trade below the level.
    """

    try:
        close = float(candle["close"])

    except (KeyError, TypeError, ValueError):
        return False

    if direction == "BUY":
        return close > level

    if direction == "SELL":
        return close < level

    return False


# ==========================================================
# FRESH LEVEL DETECTOR
# ==========================================================

def detect_fresh_level(
    df: pd.DataFrame,
    level: float,
    direction: str,
    level_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Detect whether an H4 level remains completely fresh.

    Parameters
    ----------
    df:
        H4 OHLCV dataframe.

    level:
        Price level being tested.

    direction:
        BUY or SELL.

    level_index:
        Positional index of the candle that created the level.

    Important
    ---------
    The candle that created the level is NOT considered a
    mitigation.

    Every candle after the creation candle is checked.
    """

    # ------------------------------------------------------
    # BASIC VALIDATION
    # ------------------------------------------------------

    if df is None:

        return invalid_result(
            "No H4 market data"
        )

    if len(df) < MIN_REQUIRED_CANDLES:

        return invalid_result(
            "Insufficient H4 candles"
        )

    if level is None:

        return invalid_result(
            "Level is None"
        )

    if direction not in ("BUY", "SELL"):

        return invalid_result(
            "Invalid direction"
        )

    try:
        level = float(level)

    except (TypeError, ValueError):

        return invalid_result(
            "Invalid level"
        )

    # ------------------------------------------------------
    # LEVEL CREATION INDEX IS REQUIRED
    # ------------------------------------------------------

    if level_index is None:

        return invalid_result(
            "Level creation index required"
        )

    try:
        level_index = int(level_index)

    except (TypeError, ValueError):

        return invalid_result(
            "Invalid level creation index"
        )

    if level_index < 0 or level_index >= len(df):

        return invalid_result(
            "Level creation index out of range"
        )

    # ------------------------------------------------------
    # CANDLES AFTER LEVEL CREATION
    # ------------------------------------------------------

    future_candles = df.iloc[level_index + 1:]

    if future_candles.empty:

        return invalid_result(
            "No candles after level creation"
        )

    # ------------------------------------------------------
    # PRICE MUST MOVE AWAY
    # ------------------------------------------------------

    moved_away = False

    # ------------------------------------------------------
    # CHECK EVERY FUTURE CANDLE
    # ------------------------------------------------------

    for position, (_, candle) in enumerate(
        future_candles.iterrows(),
        start=level_index + 1,
    ):

        # --------------------------------------------------
        # ANY TOUCH = MITIGATION
        # --------------------------------------------------

        if candle_touches_level(
            candle,
            level,
        ):

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "Fresh level already touched",
                "mitigated_index": position,
            }

        # --------------------------------------------------
        # PRICE MOVED AWAY
        # --------------------------------------------------

        if price_moved_away(
            candle,
            level,
            direction,
        ):

            moved_away = True

    # ------------------------------------------------------
    # PRICE MUST HAVE LEFT THE LEVEL
    # ------------------------------------------------------

    if not moved_away:

        return invalid_result(
            "Price has not moved away from level"
        )

    # ------------------------------------------------------
    # LEVEL IS FRESH
    # ------------------------------------------------------

    return {
        "valid": True,
        "entry_type": "FRESH_LEVEL",
        "entry": float(level),
        "confidence": DEFAULT_CONFIDENCE,
        "reason": "Untouched Fresh H4 Level",
        "level_index": level_index,
    }
