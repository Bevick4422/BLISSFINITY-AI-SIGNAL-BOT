"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Break & Retest Engine v1
=====================================================
"""

from __future__ import annotations

import traceback
from typing import Dict

import pandas as pd


MIN_REQUIRED_CANDLES = 5


def detect_break_retest(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict:
    """
    Detect a Break & Retest setup.

    BUY
        Break above resistance
        ↓
        Retest resistance as support
        ↓
        Bullish continuation

    SELL
        Break below support
        ↓
        Retest support as resistance
        ↓
        Bearish continuation
    """

    try:

        if df is None or len(df) < MIN_REQUIRED_CANDLES:

            return {
                "valid": False,
                "entry_type": None,
                "confidence": 0,
                "reason": "Not enough candles",
            }

        breakout = False

        for _, candle in df.iterrows():

            close = float(candle["close"])
            high = float(candle["high"])
            low = float(candle["low"])

            # -----------------------------------------
            # BREAKOUT
            # -----------------------------------------

            if not breakout:

                if direction == "BUY" and close > level:
                    breakout = True
                    continue

                if direction == "SELL" and close < level:
                    breakout = True
                    continue

            # -----------------------------------------
            # RETEST
            # -----------------------------------------

            if breakout:

                touched = low <= level <= high

                if not touched:
                    continue

                if direction == "BUY" and close > level:

                    return {

                        "valid": True,

                        "entry_type": "BREAK_RETEST",

                        "entry": round(level, 4),

                        "confidence": 90,

                        "reason": "Breakout followed by successful retest",

                    }

                if direction == "SELL" and close < level:

                    return {

                        "valid": True,

                        "entry_type": "BREAK_RETEST",

                        "entry": round(level, 4),

                        "confidence": 90,

                        "reason": "Breakdown followed by successful retest",

                    }

        return {

            "valid": False,

            "entry_type": None,

            "confidence": 0,

            "reason": "No Break & Retest",

        }

    except Exception as e:

        print("\n" + "=" * 60)
        print("BREAK & RETEST ENGINE ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return {

            "valid": False,

            "entry_type": None,

            "confidence": 0,

            "reason": "Engine Error",

        }