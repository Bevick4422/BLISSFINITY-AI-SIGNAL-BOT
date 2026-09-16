"""
BLISSFINITY SIGNAL
H4 Structure + Key Level + BOS Engine

LOCKED STRATEGY RULES
---------------------
1. H4 is used for continuation, structure, BOS and actionable entry.
2. Only completed H4 candles may participate in BOS detection.
3. Bearish BOS:
       most recent valid structural HIGH
           -> LOW that created that HIGH
           -> H4 Key Level = that LOW
           -> completed H4 BODY crosses the Key Level
           -> candle CLOSES below the Key Level
4. Bullish BOS:
       most recent valid structural LOW
           -> HIGH that created that LOW
           -> H4 Key Level = that HIGH
           -> completed H4 BODY crosses the Key Level
           -> candle CLOSES above the Key Level
5. Wick-only breaks are invalid.
6. No 60% body/range threshold is used.
7. The most recent valid structural extreme is selected.
8. The engine reports one current BOS event; it does not manufacture
   a BOS from a random nearby high/low.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


MIN_CANDLES = 12
SWING_LEFT = 2
SWING_RIGHT = 2


def _no_bos(reason: str) -> Dict[str, Any]:
    return {
        "bos": False,
        "direction": None,
        "broken_level": None,
        "key_level": None,
        "key_level_type": None,
        "key_level_index": None,
        "key_level_timestamp": None,
        "structural_extreme": None,
        "structural_extreme_index": None,
        "structural_extreme_timestamp": None,
        "break_index": None,
        "break_timestamp": None,
        "break_price": None,
        "bos_candle": None,
        "body_crossed": False,
        "close_beyond": False,
        "reason": reason,
    }


def _validate_dataframe(df: pd.DataFrame) -> Optional[str]:
    if df is None:
        return "No H4 market data"

    if len(df) < MIN_CANDLES:
        return "Insufficient completed H4 candles"

    required = {"open", "high", "low", "close", "volume"}
    missing = required.difference(df.columns)

    if missing:
        return f"Missing H4 columns: {sorted(missing)}"

    return None


def _is_swing_high(
    df: pd.DataFrame,
    index: int,
) -> bool:
    price = float(df.iloc[index]["high"])

    left = df.iloc[index - SWING_LEFT:index]["high"]
    right = df.iloc[index + 1:index + 1 + SWING_RIGHT]["high"]

    return (
        len(left) == SWING_LEFT
        and len(right) == SWING_RIGHT
        and price > float(left.max())
        and price >= float(right.max())
    )


def _is_swing_low(
    df: pd.DataFrame,
    index: int,
) -> bool:
    price = float(df.iloc[index]["low"])

    left = df.iloc[index - SWING_LEFT:index]["low"]
    right = df.iloc[index + 1:index + 1 + SWING_RIGHT]["low"]

    return (
        len(left) == SWING_LEFT
        and len(right) == SWING_RIGHT
        and price < float(left.min())
        and price <= float(right.min())
    )


def find_structural_highs(
    df: pd.DataFrame,
) -> list[Dict[str, Any]]:
    """Return confirmed structural highs in chronological order."""
    highs: list[Dict[str, Any]] = []

    last_confirmable = len(df) - 1 - SWING_RIGHT

    for index in range(SWING_LEFT, last_confirmable + 1):
        if not _is_swing_high(df, index):
            continue

        candle = df.iloc[index]

        highs.append(
            {
                "index": index,
                "timestamp": df.index[index],
                "price": float(candle["high"]),
                "open": float(candle["open"]),
                "high": float(candle["high"]),
                "low": float(candle["low"]),
                "close": float(candle["close"]),
            }
        )

    return highs


def find_structural_lows(
    df: pd.DataFrame,
) -> list[Dict[str, Any]]:
    """Return confirmed structural lows in chronological order."""
    lows: list[Dict[str, Any]] = []

    last_confirmable = len(df) - 1 - SWING_RIGHT

    for index in range(SWING_LEFT, last_confirmable + 1):
        if not _is_swing_low(df, index):
            continue

        candle = df.iloc[index]

        lows.append(
            {
                "index": index,
                "timestamp": df.index[index],
                "price": float(candle["low"]),
                "open": float(candle["open"]),
                "high": float(candle["high"]),
                "low": float(candle["low"]),
                "close": float(candle["close"]),
            }
        )

    return lows


def _find_low_that_created_high(
    df: pd.DataFrame,
    high_index: int,
) -> Optional[Dict[str, Any]]:
    """
    Find the structural LOW preceding the selected HIGH.

    The low is the protected level that must break for bearish BOS.
    """
    lows = find_structural_lows(df)

    candidates = [
        low
        for low in lows
        if low["index"] < high_index
    ]

    if not candidates:
        return None

    return candidates[-1]


def _find_high_that_created_low(
    df: pd.DataFrame,
    low_index: int,
) -> Optional[Dict[str, Any]]:
    """
    Find the structural HIGH preceding the selected LOW.

    The high is the protected level that must break for bullish BOS.
    """
    highs = find_structural_highs(df)

    candidates = [
        high
        for high in highs
        if high["index"] < low_index
    ]

    if not candidates:
        return None

    return candidates[-1]


def _bearish_body_crosses_level(
    candle: pd.Series,
    level: float,
) -> bool:
    """
    Bearish full-body break.

    The candle body must start at/above the level and close below it.
    A wick below the level while the body remains above is invalid.
    """
    open_price = float(candle["open"])
    close_price = float(candle["close"])

    return (
        close_price < level
        and open_price >= level
    )


def _bullish_body_crosses_level(
    candle: pd.Series,
    level: float,
) -> bool:
    """
    Bullish full-body break.

    The candle body must start at/below the level and close above it.
    A wick above the level while the body remains below is invalid.
    """
    open_price = float(candle["open"])
    close_price = float(candle["close"])

    return (
        close_price > level
        and open_price <= level
    )


def _serialise_candle(
    candle: pd.Series,
    index: int,
    timestamp: Any,
) -> Dict[str, Any]:
    return {
        "index": index,
        "timestamp": timestamp,
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"]),
        "volume": float(candle["volume"]),
    }


def detect_h4_bos(
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Detect the current H4 BOS.

    IMPORTANT:
    This function expects a dataframe containing COMPLETED H4 candles only.

    It deliberately does not apply a percentage body-size threshold.
    """
    validation_error = _validate_dataframe(df)

    if validation_error:
        return _no_bos(validation_error)

    # Defensive copy. The production data layer is expected to have
    # already removed forming candles.
    closed = df.copy()

    if closed.empty:
        return _no_bos("No completed H4 candles")

    # ----------------------------------------------------------
    # SELECT MOST RECENT VALID STRUCTURAL HIGH
    # ----------------------------------------------------------
    highs = find_structural_highs(closed)

    if highs:
        latest_high = highs[-1]

        protected_low = _find_low_that_created_high(
            closed,
            latest_high["index"],
        )

        if protected_low is not None:
            level = protected_low["price"]

            # Search only candles AFTER the protected structure.
            # A BOS must be caused by a later completed candle.
            for break_index in range(
                protected_low["index"] + 1,
                len(closed),
            ):
                candle = closed.iloc[break_index]

                if _bearish_body_crosses_level(
                    candle,
                    level,
                ):
                    return {
                        "bos": True,
                        "direction": "SELL",
                        "broken_level": level,
                        "key_level": level,
                        "key_level_type": "PROTECTED_LOW",
                        "key_level_index": protected_low["index"],
                        "key_level_timestamp": protected_low["timestamp"],
                        "structural_extreme": latest_high["price"],
                        "structural_extreme_index": latest_high["index"],
                        "structural_extreme_timestamp": latest_high["timestamp"],
                        "break_index": break_index,
                        "break_timestamp": closed.index[break_index],
                        "break_price": float(candle["close"]),
                        "bos_candle": _serialise_candle(
                            candle,
                            break_index,
                            closed.index[break_index],
                        ),
                        "body_crossed": True,
                        "close_beyond": True,
                        "reason": "Completed H4 body broke protected low",
                    }

    # ----------------------------------------------------------
    # SELECT MOST RECENT VALID STRUCTURAL LOW
    # ----------------------------------------------------------
    lows = find_structural_lows(closed)

    if lows:
        latest_low = lows[-1]

        protected_high = _find_high_that_created_low(
            closed,
            latest_low["index"],
        )

        if protected_high is not None:
            level = protected_high["price"]

            for break_index in range(
                protected_high["index"] + 1,
                len(closed),
            ):
                candle = closed.iloc[break_index]

                if _bullish_body_crosses_level(
                    candle,
                    level,
                ):
                    return {
                        "bos": True,
                        "direction": "BUY",
                        "broken_level": level,
                        "key_level": level,
                        "key_level_type": "PROTECTED_HIGH",
                        "key_level_index": protected_high["index"],
                        "key_level_timestamp": protected_high["timestamp"],
                        "structural_extreme": latest_low["price"],
                        "structural_extreme_index": latest_low["index"],
                        "structural_extreme_timestamp": latest_low["timestamp"],
                        "break_index": break_index,
                        "break_timestamp": closed.index[break_index],
                        "break_price": float(candle["close"]),
                        "bos_candle": _serialise_candle(
                            candle,
                            break_index,
                            closed.index[break_index],
                        ),
                        "body_crossed": True,
                        "close_beyond": True,
                        "reason": "Completed H4 body broke protected high",
                    }

    return _no_bos(
        "No completed H4 body break of the relevant protected Key Level"
    )


__all__ = [
    "detect_h4_bos",
    "find_structural_highs",
    "find_structural_lows",
]
