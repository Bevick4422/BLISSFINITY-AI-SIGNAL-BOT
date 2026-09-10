"""
BLISSFINITY SIGNAL
Break & Retest Entry Detection

BUY:
    1. Strong close above the V/A level.
    2. Price returns and touches the level.
    3. Retest candle closes back above the level.
    4. A close below the level invalidates the sequence.

SELL:
    1. Strong close below the V/A level.
    2. Price returns and touches the level.
    3. Retest candle closes back below the level.
    4. A close above the level invalidates the sequence.

Important:
    A wick touching the level counts as a retest.
    A body touching the level also counts as a retest.

The detector searches from the most recent candles backward so that
an old historical setup is not incorrectly returned as the current entry.
"""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd


MIN_REQUIRED_CANDLES = 5
BODY_CLOSE_PERCENT = 0.60


# ==========================================================
# STRONG BREAK CANDLE
# ==========================================================

def is_strong_break_candle(candle) -> bool:
    """
    Require the breakout candle to have a body covering at least
    60% of its total candle range.
    """

    try:
        high = float(candle["high"])
        low = float(candle["low"])
        open_price = float(candle["open"])
        close = float(candle["close"])

        total_range = high - low

        if total_range <= 0:
            return False

        body = abs(close - open_price)

        return (body / total_range) >= BODY_CLOSE_PERCENT

    except (KeyError, TypeError, ValueError):
        return False


# ==========================================================
# LEVEL TOUCH
# ==========================================================

def candle_touches_level(candle, level: float) -> bool:
    """
    True when the candle wick or body reaches the level.
    """

    try:
        low = float(candle["low"])
        high = float(candle["high"])

        return low <= level <= high

    except (KeyError, TypeError, ValueError):
        return False


# ==========================================================
# BREAK CONFIRMATION
# ==========================================================

def confirms_break(
    candle,
    level: float,
    direction: str,
) -> bool:
    """
    Confirm a valid structural break.

    BUY:
        Strong bullish close above level.

    SELL:
        Strong bearish close below level.
    """

    if not is_strong_break_candle(candle):
        return False

    try:
        open_price = float(candle["open"])
        close = float(candle["close"])

    except (KeyError, TypeError, ValueError):
        return False

    if direction == "BUY":

        return (
            close > level
            and close > open_price
        )

    if direction == "SELL":

        return (
            close < level
            and close < open_price
        )

    return False


# ==========================================================
# RETEST INVALIDATION
# ==========================================================

def retest_invalidates(
    candle,
    level: float,
    direction: str,
) -> bool:
    """
    Determine whether the retest has invalidated the setup.

    BUY:
        Close below level = invalid.

    SELL:
        Close above level = invalid.

    Wick through the level alone does NOT invalidate the setup.
    """

    try:
        close = float(candle["close"])

    except (KeyError, TypeError, ValueError):
        return True

    if direction == "BUY":

        return close < level

    if direction == "SELL":

        return close > level

    return True


# ==========================================================
# RETEST CONFIRMATION
# ==========================================================

def confirms_retest(
    candle,
    level: float,
    direction: str,
) -> bool:
    """
    Confirm that price touched the level and closed back
    on the correct side.
    """

    if not candle_touches_level(candle, level):
        return False

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
# BREAK & RETEST ENGINE
# ==========================================================

def detect_break_retest(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict:
    """
    Detect the most recent valid Break & Retest setup.

    Sequence:

        BREAK
          ↓
        RETEST
          ↓
        CONFIRMATION
          ↓
        ENTRY

    Returns a structured result compatible with the entry selector.
    """

    try:

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if df is None:

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "No H4 market data",
            }

        if len(df) < MIN_REQUIRED_CANDLES:

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "Not enough H4 candles",
            }

        if level is None:

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "Level is None",
            }

        if direction not in ("BUY", "SELL"):

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "Invalid direction",
            }

        level = float(level)

        # --------------------------------------------------
        # SEARCH MOST RECENT SEQUENCE
        # --------------------------------------------------

        candles = df.reset_index(drop=False)

        break_index: Optional[int] = None

        # Start from the oldest candle that can still leave
        # enough candles for a retest.
        for i in range(len(candles) - 2, -1, -1):

            candle = candles.iloc[i]

            if confirms_break(
                candle,
                level,
                direction,
            ):

                break_index = i
                break

        # --------------------------------------------------
        # NO BREAK
        # --------------------------------------------------

        if break_index is None:

            return {
                "valid": False,
                "entry_type": None,
                "entry": None,
                "confidence": 0,
                "reason": "No valid breakout",
            }

        # --------------------------------------------------
        # SEARCH FOR RETEST AFTER BREAK
        # --------------------------------------------------

        for i in range(
            break_index + 1,
            len(candles),
        ):

            candle = candles.iloc[i]

            # ----------------------------------------------
            # INVALIDATION
            # ----------------------------------------------

            if retest_invalidates(
                candle,
                level,
                direction,
            ):

                return {
                    "valid": False,
                    "entry_type": None,
                    "entry": None,
                    "confidence": 0,
                    "reason": "Retest invalidated by close",
                    "break_index": break_index,
                    "invalidated_index": i,
                }

            # ----------------------------------------------
            # VALID RETEST
            # ----------------------------------------------

            if confirms_retest(
                candle,
                level,
                direction,
            ):

                return {
                    "valid": True,
                    "entry_type": "BREAK_RETEST",
                    "entry": float(level),
                    "confidence": 90,
                    "reason": (
                        "Breakout → Level Touch → "
                        "Successful Retest"
                    ),
                    "break_index": break_index,
                    "retest_index": i,
                }

        # --------------------------------------------------
        # BREAK EXISTS BUT NO RETEST
        # --------------------------------------------------

        return {
            "valid": False,
            "entry_type": None,
            "entry": None,
            "confidence": 0,
            "reason": "Break confirmed but no retest",
            "break_index": break_index,
        }

    except Exception as exc:

        return {
            "valid": False,
            "entry_type": None,
            "entry": None,
            "confidence": 0,
            "reason": f"Break & Retest error: {exc}",
        }
