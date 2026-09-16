"""
BLISSFINITY SIGNAL — CHOCH Entry

LOCKED RULES
------------
- CHOCH is a direction-changing event.
- Bearish CHOCH = break of the protected structural LOW that created
  the prior HIGH.
- Bullish CHOCH = break of the protected structural HIGH that created
  the prior LOW.
- The protected area must be broken by an engulfing candle.
- Bearish CHOCH requires a Bearish Engulfing candle.
- Bullish CHOCH requires a Bullish Engulfing candle.
- Entry is allowed on the engulfing CHOCH candle close OR on a retest.
- Retest is optional.
- Retest only requires wick touch/penetration.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": "CHOCH",
        "entry": None,
        "direction": None,
        "protected_level": None,
        "choch_index": None,
        "retest_index": None,
        "stop_reference": None,
        "reason": reason,
    }


def _body_color(candle: pd.Series) -> str | None:
    o = float(candle["open"])
    c = float(candle["close"])

    if c > o:
        return "GREEN"
    if c < o:
        return "RED"
    return None


def _engulfs(previous: pd.Series, current: pd.Series) -> bool:
    previous_color = _body_color(previous)
    current_color = _body_color(current)

    if previous_color == "RED" and current_color == "GREEN":
        return (
            float(current["open"]) <= float(previous["close"])
            and float(current["close"]) >= float(previous["open"])
        )

    if previous_color == "GREEN" and current_color == "RED":
        return (
            float(current["open"]) >= float(previous["close"])
            and float(current["close"]) <= float(previous["open"])
        )

    return False


def _touches(candle: pd.Series, level: float) -> bool:
    return float(candle["low"]) <= level <= float(candle["high"])


def detect_choch(
    df: pd.DataFrame,
    protected_level: float,
    direction: str,
    protected_index: int,
) -> Dict[str, Any]:
    if df is None or len(df) < 2:
        return _invalid("Insufficient completed H4 candles")

    if direction not in ("BUY", "SELL"):
        return _invalid("Invalid direction")

    try:
        protected_level = float(protected_level)
        protected_index = int(protected_index)
    except (TypeError, ValueError):
        return _invalid("Invalid protected level/index")

    if protected_index < 0 or protected_index >= len(df):
        return _invalid("Protected level index out of range")

    for index in range(protected_index + 1, len(df)):
        current = df.iloc[index]
        previous = df.iloc[index - 1]

        current_color = _body_color(current)

        bullish = (
            direction == "BUY"
            and current_color == "GREEN"
            and float(current["open"]) <= protected_level
            and float(current["close"]) > protected_level
            and _engulfs(previous, current)
        )

        bearish = (
            direction == "SELL"
            and current_color == "RED"
            and float(current["open"]) >= protected_level
            and float(current["close"]) < protected_level
            and _engulfs(previous, current)
        )

        if not (bullish or bearish):
            continue

        # Entry on CHOCH candle close is valid immediately.
        return {
            "valid": True,
            "entry_type": "CHOCH_CLOSE",
            "entry": float(current["close"]),
            "direction": direction,
            "protected_level": protected_level,
            "choch_index": index,
            "retest_index": None,
            "stop_reference": {
                "type": "PROTECTED_STRUCTURE_WICK",
                "protected_index": protected_index,
            },
            "reason": "Engulfing candle broke protected structure",
        }

    return _invalid(
        "No valid engulfing CHOCH break found"
    )
