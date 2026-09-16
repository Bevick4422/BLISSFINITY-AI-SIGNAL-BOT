"""
BLISSFINITY SIGNAL
Daily Key Level Detection

V Shape
-------
Latest confirmed local swing low followed by
bullish confirmation.

A Shape
-------
Latest confirmed local swing high followed by
bearish confirmation.

The engine returns BOTH:

    level
    level_index

level_index is always the POSITIONAL integer index
inside the original dataframe.

This keeps the Daily Setup, Fresh Level, Entry
Selector, and Strategy Engine consistent.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


LOOKBACK = 30


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _empty_result() -> Optional[Dict[str, Any]]:
    return None


def _get_scan_range(length: int):
    """
    Return the valid positional range for V/A detection.

    The first and last candle cannot be the middle
    candle because both left and right candles are required.
    """

    if length < 4:
        return range(0)

    start = length - LOOKBACK
    if start < 0:
        start = 0

    end = length - 1

    return range(
        end - 1,
        start,
        -1,
    )


# ==========================================================
# V SHAPE
# ==========================================================

def _find_v_shape_info(df):
    """
    Find the latest confirmed V-shape support.

    Returns:

        {
            "level": float,
            "index": int,
        }

    The index is always a positional dataframe index,
    never a timestamp.
    """

    if df is None:
        return None

    if len(df) < 4:
        return None

    candles = df.tail(
        LOOKBACK
    )

    # Position of the first candle in the original dataframe.
    offset = len(df) - len(candles)

    for i in range(
        len(candles) - 2,
        1,
        -1,
    ):

        left = candles.iloc[i - 1]
        middle = candles.iloc[i]
        right = candles.iloc[i + 1]

        if (
            float(middle["low"])
            < float(left["low"])
            and
            float(middle["low"])
            < float(right["low"])
            and
            float(right["close"])
            > float(right["open"])
        ):

            original_position = (
                offset + i
            )

            return {
                "level": float(
                    middle["low"]
                ),
                "index": int(
                    original_position
                ),
            }

    return None


# ==========================================================
# A SHAPE
# ==========================================================

def _find_a_shape_info(df):
    """
    Find the latest confirmed A-shape resistance.

    Returns:

        {
            "level": float,
            "index": int,
        }

    The index is always a positional dataframe index,
    never a timestamp.
    """

    if df is None:
        return None

    if len(df) < 4:
        return None

    candles = df.tail(
        LOOKBACK
    )

    offset = len(df) - len(candles)

    for i in range(
        len(candles) - 2,
        1,
        -1,
    ):

        left = candles.iloc[i - 1]
        middle = candles.iloc[i]
        right = candles.iloc[i + 1]

        if (
            float(middle["high"])
            > float(left["high"])
            and
            float(middle["high"])
            > float(right["high"])
            and
            float(right["close"])
            < float(right["open"])
        ):

            original_position = (
                offset + i
            )

            return {
                "level": float(
                    middle["high"]
                ),
                "index": int(
                    original_position
                ),
            }

    return None


# ==========================================================
# PUBLIC V SHAPE
# ==========================================================

def find_v_shape(df):
    """
    Return the latest V-shape support price.
    """

    info = _find_v_shape_info(
        df
    )

    if info is None:
        return None

    return info["level"]


# ==========================================================
# PUBLIC A SHAPE
# ==========================================================

def find_a_shape(df):
    """
    Return the latest A-shape resistance price.
    """

    info = _find_a_shape_info(
        df
    )

    if info is None:
        return None

    return info["level"]


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "_find_v_shape_info",
    "_find_a_shape_info",
    "find_v_shape",
    "find_a_shape",
]