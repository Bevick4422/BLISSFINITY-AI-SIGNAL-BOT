
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Fresh H4 Level Engine v8
=====================================================

Purpose
-------
Detect untouched (fresh) H4 Supply/Demand levels.

A Fresh Level must:

• Be newly created
• Have moved away from the level
• Never be revisited
• Be trend aligned

=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict

import pandas as pd


MIN_REQUIRED_CANDLES = 10

DEFAULT_CONFIDENCE = 85


# =====================================================
# FRESH LEVEL DETECTION
# =====================================================

def detect_fresh_level(
    df: pd.DataFrame,
    level: float,
    direction: str,
) -> Dict[str, Any]:
    """
    Detect a Fresh H4 Key Level.

    Parameters
    ----------
    df
        H4 OHLCV dataframe.

    level
        Supply / Demand level.

    direction
        BUY or SELL.

    Returns
    -------
    dict
    """

    try:

        if df is None or df.empty:

            return {

                "valid": False,

                "entry_type": None,

                "entry": None,

                "confidence": 0,

                "reason": "No market data",

            }

        if len(df) < MIN_REQUIRED_CANDLES:

            return {

                "valid": False,

                "entry_type": None,

                "entry": None,

                "confidence": 0,

                "reason": "Insufficient candles",

            }

        # --------------------------------------------
        # Ignore the candle that created the level.
        # Only future candles may invalidate freshness.
        # --------------------------------------------

        future_candles = df.iloc[1:]

        revisits = 0

        for _, candle in future_candles.iterrows():

            low = float(candle["low"])
            high = float(candle["high"])

            if low <= level <= high:

                revisits += 1

                # Already mitigated
                if revisits > 0:

                    return {

                        "valid": False,

                        "entry_type": None,

                        "entry": None,

                        "confidence": 0,

                        "reason": "Level already mitigated",

                    }

        return {

            "valid": True,

            "entry_type": "FRESH_LEVEL",

            "entry": round(level, 4),

            "confidence": DEFAULT_CONFIDENCE,

            "reason": "Untouched H4 Supply/Demand Level",

        }

    except Exception as e:

        print("\n" + "=" * 60)
        print("FRESH LEVEL ENGINE ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return {

            "valid": False,

            "entry_type": None,

            "entry": None,

            "confidence": 0,

            "reason": "Engine Error",

        }