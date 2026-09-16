"""
BLISSFINITY SIGNAL
Structural Stop Loss Engine

Strategy source of truth:
- No ATR stop-loss buffers.
- No arbitrary percentage offsets.
- Stop loss comes from the exact structural candle/wick
  that establishes the setup invalidation point.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import pandas as pd


def _valid_number(value: Any) -> bool:
    """Return True when value is a finite numeric value."""
    try:
        number = float(value)
        return math.isfinite(number)
    except (TypeError, ValueError):
        return False


def _get_row(df: pd.DataFrame, index: Any) -> Optional[pd.Series]:
    """Safely retrieve a candle by positional index."""
    if df is None or df.empty:
        return None

    try:
        position = int(index)
    except (TypeError, ValueError):
        return None

    if position < 0 or position >= len(df):
        return None

    return df.iloc[position]


def _build_result(
    valid: bool,
    stop_loss: Optional[float],
    stop_reference: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    """Create a consistent stop-loss result."""
    return {
        "valid": bool(valid),
        "stop_loss": stop_loss,
        "stop_reference": stop_reference,
        "reason": reason,
    }


def calculate_stop_loss(
    df: pd.DataFrame,
    entry: float,
    direction: str,
    stop_reference: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate structural stop loss.

    Supported structural references:

    DAILY_ENGULFING_WICK
        Uses the setup candle's low for BUY
        or high for SELL.

    H4_KEY_LEVEL_ESTABLISHING_WICK
    KEY_LEVEL_ESTABLISHING_WICK
        Uses the candle establishing the key level.

    HL_WICK
        Uses the referenced candle's low for BUY.

    LH_WICK
        Uses the referenced candle's high for SELL.

    PROTECTED_STRUCTURE_WICK
        Uses the protected structural candle's wick.

    APEX_WICK
        Uses the Apex candle's wick.

    The engine deliberately does NOT calculate an ATR buffer.
    """

    if not isinstance(df, pd.DataFrame) or df.empty:
        return _build_result(
            False,
            None,
            stop_reference or {},
            "Stop-loss dataframe is empty.",
        )

    if not _valid_number(entry):
        return _build_result(
            False,
            None,
            stop_reference or {},
            "Invalid entry price.",
        )

    if direction not in {"BUY", "SELL"}:
        return _build_result(
            False,
            None,
            stop_reference or {},
            "Direction must be BUY or SELL.",
        )

    if not isinstance(stop_reference, dict) or not stop_reference:
        return _build_result(
            False,
            None,
            stop_reference or {},
            "Missing structural stop reference. No fallback stop is allowed.",
        )

    reference_type = str(
        stop_reference.get("type", "")
    ).upper().strip()

    # Determine the structural candle position.
    index_keys = (
        "candle_index",
        "level_index",
        "protected_index",
        "apex_index",
    )

    candle_index = None

    for key in index_keys:
        if key in stop_reference:
            candle_index = stop_reference.get(key)
            break

    if candle_index is None:
        return _build_result(
            False,
            None,
            stop_reference,
            "Structural stop reference has no candle index.",
        )

    candle = _get_row(df, candle_index)

    if candle is None:
        return _build_result(
            False,
            None,
            stop_reference,
            "Referenced structural candle does not exist.",
        )

    high = candle.get("high")
    low = candle.get("low")

    if not _valid_number(high) or not _valid_number(low):
        return _build_result(
            False,
            None,
            stop_reference,
            "Referenced structural candle has invalid OHLC data.",
        )

    high = float(high)
    low = float(low)
    entry = float(entry)

    # ------------------------------------------------------------------
    # BUY
    # ------------------------------------------------------------------
    if direction == "BUY":
        if reference_type in {
            "DAILY_ENGULFING_WICK",
            "HL_WICK",
            "H4_KEY_LEVEL_ESTABLISHING_WICK",
            "KEY_LEVEL_ESTABLISHING_WICK",
            "PROTECTED_STRUCTURE_WICK",
            "APEX_WICK",
            "STRUCTURAL_WICK",
        }:
            stop_loss = low
        else:
            return _build_result(
                False,
                None,
                stop_reference,
                f"Unsupported BUY stop reference type: {reference_type}",
            )

        if not math.isfinite(stop_loss):
            return _build_result(
                False,
                None,
                stop_reference,
                "Calculated BUY stop is not finite.",
            )

        if stop_loss >= entry:
            return _build_result(
                False,
                stop_loss,
                stop_reference,
                "Invalid BUY stop: stop loss must be below entry.",
            )

        return _build_result(
            True,
            stop_loss,
            stop_reference,
            "BUY stop taken from the specified structural wick.",
        )

    # ------------------------------------------------------------------
    # SELL
    # ------------------------------------------------------------------
    if reference_type in {
        "DAILY_ENGULFING_WICK",
        "LH_WICK",
        "H4_KEY_LEVEL_ESTABLISHING_WICK",
        "KEY_LEVEL_ESTABLISHING_WICK",
        "PROTECTED_STRUCTURE_WICK",
        "APEX_WICK",
        "STRUCTURAL_WICK",
    }:
        stop_loss = high
    else:
        return _build_result(
            False,
            None,
            stop_reference,
            f"Unsupported SELL stop reference type: {reference_type}",
        )

    if not math.isfinite(stop_loss):
        return _build_result(
            False,
            stop_loss,
            stop_reference,
            "Calculated SELL stop is not finite.",
        )

    if stop_loss <= entry:
        return _build_result(
            False,
            stop_loss,
            stop_reference,
            "Invalid SELL stop: stop loss must be above entry.",
        )

    return _build_result(
        True,
        stop_loss,
        stop_reference,
        "SELL stop taken from the specified structural wick.",
    )