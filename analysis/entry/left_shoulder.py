
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Left Shoulder Engine v7
=====================================================
"""

from __future__ import annotations

import traceback
from typing import Dict

import pandas as pd


BODY_CLOSE_PERCENT = 0.60
MIN_REQUIRED_CANDLES = 10


# =====================================================
# FULL BODY CANDLE
# =====================================================

def is_full_body_candle(candle) -> bool:
    """
    True if candle body is at least 60% of total range.
    """

    try:

        body = abs(float(candle["close"]) - float(candle["open"]))
        total = float(candle["high"]) - float(candle["low"])

        if total <= 0:
            return False

        return (body / total) >= BODY_CLOSE_PERCENT

    except Exception:

        return False


# =====================================================
# BREAK DETECTION
# =====================================================

def detect_break(
    level: float,
    candle,
    direction: str,
) -> bool:
    """
    Detect a valid structure break using a strong candle.
    """

    if not is_full_body_candle(candle):
        return False

    close = float(candle["close"])

    if direction == "BUY":
        return close > level

    if direction == "SELL":
        return close < level

    return False


# =====================================================
# PULLBACK DETECTION
# =====================================================

def detect_pullback(
    level: float,
    candle,
) -> bool:
    """
    True if price revisits the broken level.
    """

    low = float(candle["low"])
    high = float(candle["high"])

    return low <= level <= high


# =====================================================
# LEFT SHOULDER DETECTION
# =====================================================

def detect_left_shoulder(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict:
    """
    Detect a valid Left Shoulder.

    Sequence

    Break #1
        ↓
    Pullback
        ↓
    Break #2
        ↓
    Left Shoulder confirmed
    """

    try:

        if df is None or len(df) < MIN_REQUIRED_CANDLES:

            return {
                "valid": False,
                "entry_type": None,
                "left_shoulder": None,
                "confidence": 0,
                "reason": "Not enough candles",
            }

        break1 = False
        pullback = False

        for _, candle in df.iterrows():

            # ------------------------------------------
            # BREAK #1
            # ------------------------------------------

            if not break1:

                if detect_break(level, candle, direction):

                    break1 = True

                continue

            # ------------------------------------------
            # PULLBACK
            # ------------------------------------------

            if break1 and not pullback:

                if detect_pullback(level, candle):

                    pullback = True

                continue

            # ------------------------------------------
            # BREAK #2
            # ------------------------------------------

            if break1 and pullback:

                if detect_break(level, candle, direction):

                    return {

                        "valid": True,

                        "entry_type": "LEFT_SHOULDER",

                        "left_shoulder": round(level, 4),

                        "confidence": 95,

                        "reason": "Break1 → Pullback → Break2",

                    }

        return {

            "valid": False,

            "entry_type": None,

            "left_shoulder": None,

            "confidence": 0,

            "reason": "No Left Shoulder",

        }

    except Exception as e:

        print("\n" + "=" * 60)
        print("LEFT SHOULDER ENGINE ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return {

            "valid": False,

            "entry_type": None,

            "left_shoulder": None,

            "confidence": 0,

            "reason": "Engine Error",

        }