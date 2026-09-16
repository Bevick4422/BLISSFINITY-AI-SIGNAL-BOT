"""
BLISSFINITY SIGNAL — Break & Retest Entry

LOCKED RULES
------------
- Break uses the same H4 BOS full-body rule.
- Completed candle body must cross the level and close beyond it.
- Wick-only break is invalid.
- After the break, price must return to the broken level.
- Wick touch OR penetration is enough for the retest.
- No candle-colour or close confirmation is required.
- No retest = NO SIGNAL / never chase.
- SL reference = wick of the candle that established the broken Key Level.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": "BREAK_RETEST",
        "entry": None,
        "break_index": None,
        "retest_index": None,
        "retest_timestamp": None,
        "broken_level": None,
        "stop_reference": None,
        "reason": reason,
    }


def _body_breaks(candle: pd.Series, level: float, direction: str) -> bool:
    o = float(candle["open"])
    c = float(candle["close"])

    if direction == "SELL":
        return o >= level and c < level

    if direction == "BUY":
        return o <= level and c > level

    return False


def _touches(candle: pd.Series, level: float) -> bool:
    return float(candle["low"]) <= level <= float(candle["high"])


def detect_break_retest(
    df: pd.DataFrame,
    level: float,
    direction: str,
    level_index: Optional[int] = None,
    bos_index: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Find the retest after the supplied BOS.

    bos_index is mandatory. The function does not search for an unrelated
    break elsewhere in the dataframe.
    """
    if df is None or len(df) < 2:
        return _invalid("Insufficient completed H4 candles")

    if direction not in ("BUY", "SELL"):
        return _invalid("Invalid direction")

    if level is None:
        return _invalid("Broken level is required")

    if bos_index is None:
        return _invalid("BOS index is required")

    try:
        level = float(level)
        bos_index = int(bos_index)
    except (TypeError, ValueError):
        return _invalid("Invalid level or BOS index")

    if bos_index < 0 or bos_index >= len(df):
        return _invalid("BOS index out of range")

    if level_index is not None:
        try:
            level_index = int(level_index)
        except (TypeError, ValueError):
            return _invalid("Invalid Key Level index")

        if level_index < 0 or level_index >= len(df):
            return _invalid("Key Level index out of range")

    bos_candle = df.iloc[bos_index]

    if not _body_breaks(bos_candle, level, direction):
        return _invalid("Supplied BOS candle does not make a full-body break")

    # The retest must happen AFTER the BOS candle.
    for index in range(bos_index + 1, len(df)):
        candle = df.iloc[index]

        if _touches(candle, level):
            return {
                "valid": True,
                "entry_type": "BREAK_RETEST",
                "entry": level,
                "break_index": bos_index,
                "retest_index": index,
                "retest_timestamp": df.index[index],
                "broken_level": level,
                "stop_reference": {
                    "type": "KEY_LEVEL_ESTABLISHING_WICK",
                    "level_index": level_index,
                },
                "reason": "Post-BOS wick tap/penetration of broken level",
            }

    return _invalid(
        "Required retest has not occurred — do not chase"
    )
