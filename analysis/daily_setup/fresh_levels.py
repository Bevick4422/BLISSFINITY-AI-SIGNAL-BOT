"""
=========================================================
BLISSFINITY SIGNAL
Daily Fresh Level Engine
=========================================================

Freshness Rules:

1. V Shape creates a BUY support level.
2. A Shape creates a SELL resistance level.
3. The creation candle is excluded.
4. Every candle after creation is checked.
5. Any wick touch invalidates freshness.
6. Any body touch invalidates freshness.
7. Any penetration invalidates freshness.
8. A support remains fresh while every later low stays
   above the support level.
9. A resistance remains fresh while every later high stays
   below the resistance level.

The keylevels engine supplies a POSITIONAL candle index.
Therefore this engine uses DataFrame iloc positions directly.
=========================================================
"""

from __future__ import annotations

from typing import Any, Optional


# ==========================================================
# RESULT HELPERS
# ==========================================================

def _valid_index(
    df,
    created_index: Any,
) -> Optional[int]:
    """
    Convert the supplied creation index into a valid
    DataFrame positional index.

    keylevels.py supplies positional indexes.
    """

    if created_index is None:
        return None

    try:
        position = int(created_index)
    except (TypeError, ValueError):
        return None

    if position < 0:
        return None

    if position >= len(df):
        return None

    return position


# ==========================================================
# SUPPORT
# ==========================================================

def is_fresh_support(
    df,
    level: Any,
    created_index: Any = None,
) -> bool:
    """
    Determine whether a BUY support level is still fresh.

    Any later candle with:

        low <= level

    means the level has been touched or mitigated.

    The creation candle itself is ignored.
    """

    if df is None or len(df) == 0:
        return False

    if level is None:
        return False

    try:
        level = float(level)
    except (TypeError, ValueError):
        return False

    position = _valid_index(
        df,
        created_index,
    )

    if position is None:
        return False

    candles_after = df.iloc[position + 1:]

    # No later candle means nothing has mitigated the level.
    if candles_after.empty:
        return True

    # Any wick/body/penetration touch invalidates freshness.
    touched = (
        candles_after["low"] <= level
    ).any()

    return not bool(touched)


# ==========================================================
# RESISTANCE
# ==========================================================

def is_fresh_resistance(
    df,
    level: Any,
    created_index: Any = None,
) -> bool:
    """
    Determine whether a SELL resistance level is still fresh.

    Any later candle with:

        high >= level

    means the level has been touched or mitigated.

    The creation candle itself is ignored.
    """

    if df is None or len(df) == 0:
        return False

    if level is None:
        return False

    try:
        level = float(level)
    except (TypeError, ValueError):
        return False

    position = _valid_index(
        df,
        created_index,
    )

    if position is None:
        return False

    candles_after = df.iloc[position + 1:]

    # No later candle means nothing has mitigated the level.
    if candles_after.empty:
        return True

    # Any wick/body/penetration touch invalidates freshness.
    touched = (
        candles_after["high"] >= level
    ).any()

    return not bool(touched)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "is_fresh_support",
    "is_fresh_resistance",
]