"""
BLISSFINITY SIGNAL — Left Shoulder Entry

LOCKED SEQUENCE
--------------
BREAK #1
-> full-body close beyond level
-> pullback / attempted hold
-> level fails to hold
-> BREAK #2
-> full-body close beyond level
-> LEFT SHOULDER CONFIRMED
-> APEX
-> retrace
-> ENTRY

Rules
-----
- Both Break #1 and Break #2 require full-body close beyond the level.
- Pullback only needs to return toward the level before the second break.
- After Break #2, an Apex must form.
- Entry occurs only after the Apex and a later retrace to the broken level.
- Wick tap/penetration is sufficient for the final retest.
- SL reference = Apex high for SELL / Apex low for BUY.
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry_type": "LEFT_SHOULDER",
        "entry": None,
        "break1_index": None,
        "break2_index": None,
        "apex_index": None,
        "retest_index": None,
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


def detect_left_shoulder(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict[str, Any]:
    if df is None or len(df) < 6:
        return _invalid("Insufficient completed H4 candles")

    if direction not in ("BUY", "SELL"):
        return _invalid("Invalid direction")

    try:
        level = float(level)
    except (TypeError, ValueError):
        return _invalid("Invalid level")

    # Search chronological candidates. A later valid sequence supersedes
    # an earlier incomplete one.
    for break1 in range(0, len(df) - 4):
        candle1 = df.iloc[break1]

        if not _body_breaks(candle1, level, direction):
            continue

        # Pullback toward the broken level after Break #1.
        pullback_index = None

        for p in range(break1 + 1, len(df) - 2):
            pullback = df.iloc[p]

            if _touches(pullback, level):
                pullback_index = p
                break

        if pullback_index is None:
            continue

        # Break #2 must occur after the pullback.
        for break2 in range(pullback_index + 1, len(df) - 2):
            candle2 = df.iloc[break2]

            if not _body_breaks(candle2, level, direction):
                continue

            # The Apex must occur after Break #2 and before the final
            # retrace. We require an actual local extreme.
            for apex in range(break2 + 1, len(df) - 1):
                apex_candle = df.iloc[apex]

                if direction == "SELL":
                    is_apex = (
                        float(apex_candle["high"])
                        >= float(df.iloc[apex - 1]["high"])
                        and float(apex_candle["high"])
                        >= float(df.iloc[apex + 1]["high"])
                    )
                    apex_price = float(apex_candle["high"])
                else:
                    is_apex = (
                        float(apex_candle["low"])
                        <= float(df.iloc[apex - 1]["low"])
                        and float(apex_candle["low"])
                        <= float(df.iloc[apex + 1]["low"])
                    )
                    apex_price = float(apex_candle["low"])

                if not is_apex:
                    continue

                # Final retrace must occur after the Apex.
                for retest in range(apex + 1, len(df)):
                    retest_candle = df.iloc[retest]

                    if not _touches(retest_candle, level):
                        continue

                    return {
                        "valid": True,
                        "entry_type": "LEFT_SHOULDER",
                        "entry": level,
                        "break1_index": break1,
                        "break2_index": break2,
                        "apex_index": apex,
                        "retest_index": retest,
                        "broken_level": level,
                        "stop_reference": {
                            "type": "APEX",
                            "apex_index": apex,
                            "apex_price": apex_price,
                        },
                        "reason": (
                            "Break #1 -> pullback -> Break #2 -> "
                            "Apex -> retrace"
                        ),
                    }

    return _invalid(
        "Complete Left Shoulder sequence not formed — no signal"
    )
