"""
BLISSFINITY SIGNAL
Left Shoulder Entry Engine

Purpose:
    Detect a structural Left Shoulder entry around a confirmed
    Daily V Shape / A Shape level.

Sequence:

    Break #1
        ↓
    Pullback / Retest
        ↓
    Break #2
        ↓
    LEFT SHOULDER ENTRY

Rules:
    - BUY requires strong closes above the level.
    - SELL requires strong closes below the level.
    - Pullback must touch the key level.
    - Wick touch is sufficient for the pullback.
    - A decisive close through the level invalidates the structure.
    - Uses the most recent valid structure.
    - No EMA.
    - No indicators.
    - No arbitrary time expiry.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


# ==========================================================
# SETTINGS
# ==========================================================

BODY_CLOSE_PERCENT = 0.60
MIN_REQUIRED_CANDLES = 10


# ==========================================================
# RESULT HELPERS
# ==========================================================

def no_left_shoulder(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": None,
        "entry": None,
        "left_shoulder": None,
        "confidence": 0,
        "reason": reason,
    }


# ==========================================================
# STRONG BODY
# ==========================================================

def is_strong_body(candle: pd.Series) -> bool:
    try:
        open_price = float(candle["open"])
        close = float(candle["close"])
        high = float(candle["high"])
        low = float(candle["low"])

    except (KeyError, TypeError, ValueError):
        return False

    candle_range = high - low

    if candle_range <= 0:
        return False

    body = abs(close - open_price)

    return (
        body / candle_range
        >= BODY_CLOSE_PERCENT
    )


# ==========================================================
# STRUCTURAL BREAK
# ==========================================================

def is_break(
    candle: pd.Series,
    level: float,
    direction: str,
) -> bool:

    if direction not in ("BUY", "SELL"):
        return False

    if not is_strong_body(candle):
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

    return (
        close < level
        and close < open_price
    )


# ==========================================================
# LEVEL TOUCH
# ==========================================================

def touches_level(
    candle: pd.Series,
    level: float,
) -> bool:

    try:
        low = float(candle["low"])
        high = float(candle["high"])

    except (KeyError, TypeError, ValueError):
        return False

    return (
        low <= level <= high
    )


# ==========================================================
# INVALIDATION
# ==========================================================

def invalidates_structure(
    candle: pd.Series,
    level: float,
    direction: str,
) -> bool:

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
# LEFT SHOULDER ENGINE
# ==========================================================

def detect_left_shoulder(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict[str, Any]:

    if df is None:
        return no_left_shoulder(
            "No H4 market data"
        )

    if not isinstance(df, pd.DataFrame):
        return no_left_shoulder(
            "Invalid H4 market data"
        )

    if len(df) < MIN_REQUIRED_CANDLES:
        return no_left_shoulder(
            "Not enough H4 candles"
        )

    if direction not in ("BUY", "SELL"):
        return no_left_shoulder(
            "Invalid direction"
        )

    if level is None:
        return no_left_shoulder(
            "No key level"
        )

    try:
        level = float(level)

    except (TypeError, ValueError):
        return no_left_shoulder(
            "Invalid key level"
        )

    if level <= 0:
        return no_left_shoulder(
            "Invalid key level"
        )

    candles = df.reset_index(drop=False)

    latest = len(candles) - 1

    # ======================================================
    # SEARCH FROM MOST RECENT BREAK #2
    # ======================================================

    for break2_position in range(
        latest,
        1,
        -1,
    ):

        break2 = candles.iloc[
            break2_position
        ]

        if not is_break(
            break2,
            level,
            direction,
        ):
            continue

        # ==================================================
        # SEARCH BACKWARD FOR PULLBACK
        # ==================================================

        for pullback_position in range(
            break2_position - 1,
            0,
            -1,
        ):

            pullback = candles.iloc[
                pullback_position
            ]

            if not touches_level(
                pullback,
                level,
            ):
                continue

            # ==============================================
            # CHECK INVALIDATION BETWEEN PULLBACK AND BREAK2
            # ==============================================

            invalidated = False

            for position in range(
                pullback_position + 1,
                break2_position,
            ):

                candle = candles.iloc[
                    position
                ]

                if invalidates_structure(
                    candle,
                    level,
                    direction,
                ):

                    invalidated = True
                    break

            if invalidated:
                continue

            # ==================================================
            # SEARCH BACKWARD FOR BREAK #1
            # ==================================================

            for break1_position in range(
                pullback_position - 1,
                -1,
                -1,
            ):

                break1 = candles.iloc[
                    break1_position
                ]

                if not is_break(
                    break1,
                    level,
                    direction,
                ):
                    continue

                # ==================================================
                # CONFIRMED LEFT SHOULDER
                # ==================================================

                return {
                    "valid": True,
                    "entry_type": "LEFT_SHOULDER",
                    "entry": float(level),
                    "left_shoulder": float(level),
                    "confidence": 95,
                    "reason": (
                        "Break1 → Pullback → Break2 "
                        "Left Shoulder confirmed"
                    ),
                    "break1_index": int(
                        break1_position
                    ),
                    "pullback_index": int(
                        pullback_position
                    ),
                    "break2_index": int(
                        break2_position
                    ),
                }

    return no_left_shoulder(
        "No valid Left Shoulder structure"
    )


# ==========================================================
# EXPORT
# ==========================================================

__all__ = [
    "detect_left_shoulder",
    "is_strong_body",
    "is_break",
    "touches_level",
]