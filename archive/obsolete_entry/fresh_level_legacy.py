"""
BLISSFINITY SIGNAL — Fresh Level Entry

LOCKED RULES
------------
- Fresh Demand/Resistance means NEVER TAPPED.
- Any wick/body/exact-price touch makes the level non-fresh permanently.
- Fresh level alone is not a setup.
- An established trend is mandatory.
- Bullish: established HH/HL trend + fresh Demand -> tap -> BUY.
- Bearish: established LL/LH trend + fresh Resistance -> tap -> SELL.
- If the level is already being touched when first identified, immediate
  entry is allowed.
- SL reference is the establishing candle wick.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": "FRESH_LEVEL",
        "entry": None,
        "level": None,
        "touch_index": None,
        "stop_reference": None,
        "reason": reason,
    }


def _touches(candle: pd.Series, level: float) -> bool:
    return float(candle["low"]) <= level <= float(candle["high"])


def detect_fresh_level(
    df: pd.DataFrame,
    level: float,
    direction: str,
    level_index: Optional[int],
    trend: str,
) -> Dict[str, Any]:
    if df is None or df.empty:
        return _invalid("No completed H4 candles")

    if direction not in ("BUY", "SELL"):
        return _invalid("Invalid direction")

    expected_trend = "BULLISH" if direction == "BUY" else "BEARISH"

    if trend != expected_trend:
        return _invalid(
            f"Established {expected_trend} trend required"
        )

    if level is None:
        return _invalid("Fresh level is required")

    if level_index is None:
        return _invalid("Fresh level creation index required")

    try:
        level = float(level)
        level_index = int(level_index)
    except (TypeError, ValueError):
        return _invalid("Invalid level or level index")

    if level_index < 0 or level_index >= len(df):
        return _invalid("Level index out of range")

    # Any later candle touching the level destroys freshness.
    # The creation candle itself is excluded from historical mitigation.
    for index in range(level_index + 1, len(df)):
        candle = df.iloc[index]

        if _touches(candle, level):
            return {
                "valid": True,
                "entry_type": "FRESH_LEVEL",
                "entry": level,
                "level": level,
                "touch_index": index,
                "stop_reference": {
                    "type": "ESTABLISHING_CANDLE_WICK",
                    "level_index": level_index,
                },
                "reason": "Fresh level tap/penetration",
            }

    # If the latest available completed candle has not touched it,
    # there is no entry. We never anticipate a future touch.
    return _invalid(
        "Fresh level has not been tapped — wait, do not chase"
    )
