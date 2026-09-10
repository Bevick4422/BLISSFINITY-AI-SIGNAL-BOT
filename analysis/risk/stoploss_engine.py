"""
=====================================================
BLISSFINITY SIGNAL
Production Stop Loss Engine
=====================================================

Purpose:
    Calculate structural stop-loss placement using
    the supplied 4H market data only.

Rules:
    BUY  -> below a relevant 4H swing low
    SELL -> above a relevant 4H swing high

The engine does not use:
    - 15-minute structure
    - 1-hour structure
    - Arbitrary current-candle range
    - Generic lower-timeframe stops

The existing A/V key-level definition is preserved.
=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Optional

import pandas as pd


# Small buffer beyond the 4H structural level.
ATR_BUFFER = 0.20

# Number of candles on each side required to confirm a swing.
SWING_LOOKBACK = 2


def _validate_dataframe(df: pd.DataFrame) -> bool:
    """Confirm that the supplied market data has the required columns."""
    if df is None or df.empty:
        return False

    required_columns = {"high", "low", "close"}

    return required_columns.issubset(df.columns)


def _find_4h_swing_low(
    df: pd.DataFrame,
    entry: float,
) -> Optional[float]:
    """
    Find the most recent confirmed 4H swing low below entry.

    A swing low is a candle whose low is lower than the
    lows of the candles immediately before and after it.
    """

    if len(df) < (SWING_LOOKBACK * 2) + 1:
        return None

    for i in range(
        len(df) - SWING_LOOKBACK - 1,
        SWING_LOOKBACK - 1,
        -1,
    ):
        current_low = float(df.iloc[i]["low"])

        left_lows = [
            float(df.iloc[i - j]["low"])
            for j in range(1, SWING_LOOKBACK + 1)
        ]

        right_lows = [
            float(df.iloc[i + j]["low"])
            for j in range(1, SWING_LOOKBACK + 1)
        ]

        is_swing_low = (
            current_low < min(left_lows)
            and current_low <= min(right_lows)
        )

        if is_swing_low and current_low < entry:
            return current_low

    return None


def _find_4h_swing_high(
    df: pd.DataFrame,
    entry: float,
) -> Optional[float]:
    """
    Find the most recent confirmed 4H swing high above entry.

    A swing high is a candle whose high is higher than the
    highs of the candles immediately before and after it.
    """

    if len(df) < (SWING_LOOKBACK * 2) + 1:
        return None

    for i in range(
        len(df) - SWING_LOOKBACK - 1,
        SWING_LOOKBACK - 1,
        -1,
    ):
        current_high = float(df.iloc[i]["high"])

        left_highs = [
            float(df.iloc[i - j]["high"])
            for j in range(1, SWING_LOOKBACK + 1)
        ]

        right_highs = [
            float(df.iloc[i + j]["high"])
            for j in range(1, SWING_LOOKBACK + 1)
        ]

        is_swing_high = (
            current_high > max(left_highs)
            and current_high >= max(right_highs)
        )

        if is_swing_high and current_high > entry:
            return current_high

    return None


def calculate_stop_loss(
    df: pd.DataFrame,
    atr: float,
    direction: str,
    entry_type: str = "ENGULFING",
    entry: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate a structural stop-loss from 4H data.

    Parameters:
        df:
            The 4H dataframe supplied by the strategy engine.

        atr:
            ATR calculated from the same 4H timeframe.

        direction:
            BUY or SELL.

        entry_type:
            Existing setup type. Preserved for compatibility.

        entry:
            Trade entry price. Required for selecting the
            correct swing relative to the entry.

    Returns:
        A dictionary containing the structural stop-loss.
    """

    try:
        if not _validate_dataframe(df):
            return {
                "valid": False,
                "stop_loss": None,
                "reason": "Invalid 4H market data",
            }

        if direction not in {"BUY", "SELL"}:
            return {
                "valid": False,
                "stop_loss": None,
                "reason": "Direction must be BUY or SELL",
            }

        if entry is None:
            entry = float(df.iloc[-1]["close"])
        else:
            entry = float(entry)

        atr = max(float(atr), 0.0001)

        # Explicitly use the supplied 4H dataframe.
        h4 = df.copy()

        if direction == "BUY":
            swing_level = _find_4h_swing_low(h4, entry)

            if swing_level is None:
                return {
                    "valid": False,
                    "stop_loss": None,
                    "reason": "No valid 4H swing low below BUY entry",
                }

            stop_loss = swing_level - (atr * ATR_BUFFER)

            if stop_loss >= entry:
                return {
                    "valid": False,
                    "stop_loss": None,
                    "reason": "4H BUY stop is not below entry",
                }

            return {
                "valid": True,
                "stop_loss": round(stop_loss, 8),
                "entry_type": entry_type,
                "structure": "4H_SWING_LOW",
                "swing_level": round(swing_level, 8),
                "timeframe": "4h",
                "reason": "4H Swing Low Structural Stop",
            }

        swing_level = _find_4h_swing_high(h4, entry)

        if swing_level is None:
            return {
                "valid": False,
                "stop_loss": None,
                "reason": "No valid 4H swing high above SELL entry",
            }

        stop_loss = swing_level + (atr * ATR_BUFFER)

        if stop_loss <= entry:
            return {
                "valid": False,
                "stop_loss": None,
                "reason": "4H SELL stop is not above entry",
            }

        return {
            "valid": True,
            "stop_loss": round(stop_loss, 8),
            "entry_type": entry_type,
            "structure": "4H_SWING_HIGH",
            "swing_level": round(swing_level, 8),
            "timeframe": "4h",
            "reason": "4H Swing High Structural Stop",
        }

    except Exception as e:
        print("STOP LOSS ERROR:", e)
        traceback.print_exc()

        return {
            "valid": False,
            "stop_loss": None,
            "reason": str(e),
        }


__all__ = ["calculate_stop_loss"]