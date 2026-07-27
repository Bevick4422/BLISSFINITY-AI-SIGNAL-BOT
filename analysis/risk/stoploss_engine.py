
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Stop Loss Engine v8
=====================================================

Priority

1. Left Shoulder
2. Break & Retest
3. Fresh H4 Level
4. Engulfing

=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict

import pandas as pd


ATR_BUFFER = 0.20
LOOKBACK = 5


# =====================================================
# INTERNAL HELPERS
# =====================================================

def _buy_stop(df: pd.DataFrame, atr: float) -> float:

    swing_low = float(df["low"].min())

    return swing_low - (atr * ATR_BUFFER)


def _sell_stop(df: pd.DataFrame, atr: float) -> float:

    swing_high = float(df["high"].max())

    return swing_high + (atr * ATR_BUFFER)


# =====================================================
# STOP LOSS ENGINE
# =====================================================

def calculate_stop_loss(
    df: pd.DataFrame,
    atr: float,
    direction: str,
    entry_type: str = "ENGULFING",
) -> Dict[str, Any]:
    """
    Calculate a structure-based stop loss.

    Parameters
    ----------
    df
        Entry timeframe candles.

    atr
        Current ATR value.

    direction
        BUY / SELL

    entry_type

        LEFT_SHOULDER
        BREAK_RETEST
        FRESH_LEVEL
        ENGULFING
    """

    try:

        if df is None or df.empty:

            return {

                "valid": False,

                "stop_loss": None,

                "reason": "No market data",

            }

        if len(df) < LOOKBACK:

            return {

                "valid": False,

                "stop_loss": None,

                "reason": "Not enough candles",

            }

        recent = df.tail(LOOKBACK)

        # ==================================================
        # LEFT SHOULDER
        # ==================================================

        if entry_type == "LEFT_SHOULDER":

            stop = (
                _buy_stop(recent, atr)
                if direction == "BUY"
                else _sell_stop(recent, atr)
            )

        # ==================================================
        # BREAK & RETEST
        # ==================================================

        elif entry_type == "BREAK_RETEST":

            stop = (
                _buy_stop(recent, atr)
                if direction == "BUY"
                else _sell_stop(recent, atr)
            )

        # ==================================================
        # FRESH LEVEL
        # ==================================================

        elif entry_type == "FRESH_LEVEL":

            stop = (
                _buy_stop(recent, atr)
                if direction == "BUY"
                else _sell_stop(recent, atr)
            )

        # ==================================================
        # ENGULFING
        # ==================================================

        else:

            stop = (
                _buy_stop(recent, atr)
                if direction == "BUY"
                else _sell_stop(recent, atr)
            )

        return {

            "valid": True,

            "stop_loss": round(stop, 8),

            "entry_type": entry_type,

            "reason": f"{entry_type} Structure Stop",

        }

    except Exception as e:

        print("\n" + "=" * 60)
        print("STOP LOSS ENGINE ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return {

            "valid": False,

            "stop_loss": None,

            "reason": "Engine Error",

        }