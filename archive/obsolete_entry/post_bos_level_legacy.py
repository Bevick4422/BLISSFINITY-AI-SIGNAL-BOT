"""
BLISSFINITY SIGNAL
Post-BOS Fresh H4 Level Detection

Purpose:
    Find a new H4 supply/demand level created after
    the current H4 BOS.

This detector does not chase price and does not
generate a trading signal by itself.

SELL:
    - Search for a bearish H4 candle after the BOS.
    - Use its high as a possible supply level.
    - Require price to move below the level.
    - Reject the level if a later candle touches it.

BUY:
    - Search for a bullish H4 candle after the BOS.
    - Use its low as a possible demand level.
    - Require price to move above the level.
    - Reject the level if a later candle touches it.

The BOS candle itself is not used as the level
creation candle.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


MIN_REQUIRED_CANDLES = 3
DEFAULT_CONFIDENCE = 80


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
# CANDLE TOUCH
# ==========================================================

def candle_touches_level(
    candle,
    level: float,
) -> bool:
    """
    Any wick or body touch means the level is mitigated.
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
    BUY:
        Close must be above the demand level.

    SELL:
        Close must be below the supply level.
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
# CANDIDATE LEVEL
# ==========================================================

def get_candidate_level(
    candle,
    direction: str,
) -> Optional[float]:
    """
    Create a simple H4 structural candidate.

    SELL:
        Bearish candle high = possible supply level.

    BUY:
        Bullish candle low = possible demand level.
    """

    try:
        open_price = float(candle["open"])
        close = float(candle["close"])
        high = float(candle["high"])
        low = float(candle["low"])

    except (KeyError, TypeError, ValueError):
        return None

    if direction == "SELL":

        if close >= open_price:
            return None

        return high

    if direction == "BUY":

        if close <= open_price:
            return None

        return low

    return None


# ==========================================================
# POST-BOS FRESH LEVEL DETECTOR
# ==========================================================

def detect_post_bos_level(
    df: pd.DataFrame,
    bos_index: Any,
    direction: str,
) -> Dict[str, Any]:
    """
    Find the most recent fresh H4 level created after BOS.

    Parameters
    ----------
    df:
        H4 OHLCV dataframe.

    bos_index:
        Timestamp or positional index of the H4 BOS candle.

    direction:
        BUY or SELL.

    Notes
    -----
    The BOS candle itself is excluded.

    The newest candle is excluded as a candidate because
    it has no confirmed future candles available yet.
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

    if direction not in ("BUY", "SELL"):
        return invalid_result(
            "Invalid direction"
        )

    if bos_index is None:
        return invalid_result(
            "BOS index required"
        )

    # ------------------------------------------------------
    # COPY DATA
    # ------------------------------------------------------

    try:
        candles = df.reset_index(drop=False).copy()

    except Exception as exc:
        return invalid_result(
            f"Could not prepare H4 data: {exc}"
        )

    # ------------------------------------------------------
    # RESOLVE BOS POSITION
    # ------------------------------------------------------

    try:

        if isinstance(
            bos_index,
            (int, float),
        ):
            bos_position = int(bos_index)

        else:
            matching_positions = df.index.get_indexer(
                [bos_index]
            )

            if (
                len(matching_positions) == 0
                or matching_positions[0] < 0
            ):
                return invalid_result(
                    "BOS timestamp not found in H4 data"
                )

            bos_position = int(
                matching_positions[0]
            )

    except (
        AttributeError,
        IndexError,
        TypeError,
        ValueError,
    ) as exc:

        return invalid_result(
            f"Invalid BOS index: {exc}"
        )

    if bos_position < 0 or bos_position >= len(df):
        return invalid_result(
            "BOS index out of range"
        )

    # ------------------------------------------------------
    # SEARCH POST-BOS CANDIDATES
    # ------------------------------------------------------

    # Exclude:
    #   - BOS candle
    #   - Current/latest candle
    first_candidate = bos_position + 1
    last_candidate = len(candles) - 2

    if first_candidate > last_candidate:
        return invalid_result(
            "No confirmed candles after BOS"
        )

    for candidate_position in range(
        last_candidate,
        first_candidate - 1,
        -1,
    ):

        candidate = candles.iloc[
            candidate_position
        ]

        level = get_candidate_level(
            candidate=candidate,
            direction=direction,
        )

        if level is None:
            continue

        # --------------------------------------------------
        # PRICE MUST MOVE AWAY
        # --------------------------------------------------

        moved_away = False
        mitigated = False
        mitigated_position = None

        for future_position in range(
            candidate_position + 1,
            len(candles),
        ):

            future_candle = candles.iloc[
                future_position
            ]

            # Any later touch invalidates the level.
            if candle_touches_level(
                future_candle,
                level,
            ):
                mitigated = True
                mitigated_position = future_position
                break

            if price_moved_away(
                future_candle,
                level,
                direction,
            ):
                moved_away = True

        if mitigated:
            continue

        if not moved_away:
            continue

        # --------------------------------------------------
        # VALID POST-BOS LEVEL
        # --------------------------------------------------

        return {
            "valid": True,
            "entry_type": "POST_BOS_LEVEL",
            "entry": float(level),
            "confidence": DEFAULT_CONFIDENCE,
            "reason": (
                "Fresh H4 level formed after current BOS"
            ),
            "level_index": candidate_position,
            "bos_index": bos_position,
            "direction": direction,
        }

    # ------------------------------------------------------
    # NO VALID LEVEL
    # ------------------------------------------------------

    return invalid_result(
        "No fresh post-BOS H4 level found"
    )


__all__ = [
    "detect_post_bos_level",
    "candle_touches_level",
    "price_moved_away",
]