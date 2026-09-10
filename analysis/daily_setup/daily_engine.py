"""
=========================================================
BLISSFINITY SIGNAL
Daily Setup Engine
=========================================================

The Daily timeframe identifies the potential setup.

V/A shapes require:
    1. A valid fresh level.
    2. A confirmed directional candle.

A fresh level alone is NOT enough to create a signal.

Rules:

- Bullish Engulfing -> BUY
- Bearish Engulfing -> SELL
- Fresh V Shape + bullish confirmation -> BUY
- Fresh A Shape + bearish confirmation -> SELL
- Engulfing setups do NOT require H4 BOS.
- V/A setups still require H4 BOS in the strategy engine.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from analysis.daily_setup.engulfing import detect_engulfing

from analysis.daily_setup.keylevels import (
    _find_v_shape_info,
    _find_a_shape_info,
)

from analysis.daily_setup.fresh_levels import (
    is_fresh_support,
    is_fresh_resistance,
)


DEBUG = True


# =========================================================
# RESULT HELPERS
# =========================================================

def _invalid_setup() -> Dict[str, Any]:
    return {
        "direction": None,
        "setup": "NONE",
        "level": None,
        "level_index": None,
        "entry": None,
        "valid": False,
    }


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number <= 0:
        return None

    return number


def _safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# =========================================================
# DAILY CANDLE CONFIRMATION
# =========================================================

def _get_daily_confirmation(df) -> Dict[str, Any]:
    """
    Confirm direction using the latest closed Daily candle.

    BUY confirmation:
        Latest close > previous candle high

    SELL confirmation:
        Latest close < previous candle low

    This prevents a fresh V/A level from immediately becoming
    a directional signal without price confirmation.
    """

    result = {
        "bullish": False,
        "bearish": False,
        "latest_close": None,
        "previous_high": None,
        "previous_low": None,
    }

    if df is None or len(df) < 3:
        return result

    try:
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        latest_close = _safe_float(latest["close"])
        previous_high = _safe_float(previous["high"])
        previous_low = _safe_float(previous["low"])

        if (
            latest_close is None
            or previous_high is None
            or previous_low is None
        ):
            return result

        result["latest_close"] = latest_close
        result["previous_high"] = previous_high
        result["previous_low"] = previous_low

        result["bullish"] = latest_close > previous_high
        result["bearish"] = latest_close < previous_low

    except (KeyError, IndexError, TypeError, ValueError):
        return result

    return result


# =========================================================
# DAILY SETUP
# =========================================================

def detect_daily_setup(
    df,
) -> Dict[str, Any]:
    """
    Detect the highest-priority valid Daily setup.

    V/A setups require both:
        - Fresh support/resistance
        - Directional Daily confirmation

    The function safely handles missing detector results.
    """

    if df is None or len(df) < 3:
        return _invalid_setup()

    # =====================================================
    # 1. ENGULFING
    # =====================================================

    try:
        engulfing = detect_engulfing(df)
    except Exception as exc:
        if DEBUG:
            print(f"Engulfing detector error: {exc}")
        engulfing = {}

    if not isinstance(engulfing, dict):
        engulfing = {}

    engulfing_direction = engulfing.get("direction")
    engulfing_setup = engulfing.get("setup")

    engulfing_entry = _safe_float(
        engulfing.get("entry")
    )

    bullish_engulfing = (
        engulfing_direction == "BUY"
        and engulfing_setup == "Bullish Engulfing"
        and engulfing_entry is not None
        and engulfing.get("valid") is True
    )

    bearish_engulfing = (
        engulfing_direction == "SELL"
        and engulfing_setup == "Bearish Engulfing"
        and engulfing_entry is not None
        and engulfing.get("valid") is True
    )

    # =====================================================
    # 2. DAILY CONFIRMATION
    # =====================================================

    confirmation = _get_daily_confirmation(df)

    bullish_confirmation = confirmation["bullish"]
    bearish_confirmation = confirmation["bearish"]

    # =====================================================
    # 3. V SHAPE
    # =====================================================

    try:
        v_info = _find_v_shape_info(df)
    except Exception as exc:
        if DEBUG:
            print(f"V Shape detector error: {exc}")
        v_info = None

    if not isinstance(v_info, dict):
        v_info = None

    v_level = None
    v_index = None
    fresh_support = False

    if v_info is not None:
        v_level = _safe_float(v_info.get("level"))
        v_index = _safe_int(v_info.get("index"))

        if v_level is not None and v_index is not None:
            try:
                fresh_support = is_fresh_support(
                    df,
                    v_level,
                    v_index,
                )
            except Exception as exc:
                if DEBUG:
                    print(f"Fresh support error: {exc}")
                fresh_support = False

    # =====================================================
    # 4. A SHAPE
    # =====================================================

    try:
        a_info = _find_a_shape_info(df)
    except Exception as exc:
        if DEBUG:
            print(f"A Shape detector error: {exc}")
        a_info = None

    if not isinstance(a_info, dict):
        a_info = None

    a_level = None
    a_index = None
    fresh_resistance = False

    if a_info is not None:
        a_level = _safe_float(a_info.get("level"))
        a_index = _safe_int(a_info.get("index"))

        if a_level is not None and a_index is not None:
            try:
                fresh_resistance = is_fresh_resistance(
                    df,
                    a_level,
                    a_index,
                )
            except Exception as exc:
                if DEBUG:
                    print(f"Fresh resistance error: {exc}")
                fresh_resistance = False

    # =====================================================
    # 5. CONFIRMED SETUPS
    # =====================================================

    confirmed_v_shape = (
        fresh_support
        and bullish_confirmation
    )

    confirmed_a_shape = (
        fresh_resistance
        and bearish_confirmation
    )

    # =====================================================
    # DEBUG
    # =====================================================

    if DEBUG:
        print()
        print("=" * 60)
        print("DAILY SETUP")
        print("=" * 60)

        print(f"Bullish Engulfing : {bullish_engulfing}")
        print(f"Bearish Engulfing : {bearish_engulfing}")
        print(f"Engulfing Entry   : {engulfing_entry}")

        print(f"Latest Close      : {confirmation['latest_close']}")
        print(f"Previous High     : {confirmation['previous_high']}")
        print(f"Previous Low      : {confirmation['previous_low']}")

        print(f"Bullish Confirm   : {bullish_confirmation}")
        print(f"Bearish Confirm   : {bearish_confirmation}")

        print(f"V Shape Level     : {v_level}")
        print(f"V Shape Index     : {v_index}")
        print(f"V Shape Fresh     : {fresh_support}")
        print(f"V Shape Confirmed : {confirmed_v_shape}")

        print(f"A Shape Level     : {a_level}")
        print(f"A Shape Index     : {a_index}")
        print(f"A Shape Fresh     : {fresh_resistance}")
        print(f"A Shape Confirmed : {confirmed_a_shape}")

        print("=" * 60)

    # =====================================================
    # PRIORITY 1 — BULLISH ENGULFING
    # =====================================================

    if bullish_engulfing:
        return {
            "direction": "BUY",
            "setup": "Bullish Engulfing",
            "level": None,
            "level_index": None,
            "entry": engulfing_entry,
            "valid": True,
        }

    # =====================================================
    # PRIORITY 2 — BEARISH ENGULFING
    # =====================================================

    if bearish_engulfing:
        return {
            "direction": "SELL",
            "setup": "Bearish Engulfing",
            "level": None,
            "level_index": None,
            "entry": engulfing_entry,
            "valid": True,
        }

    # =====================================================
    # PRIORITY 3 — CONFIRMED V SHAPE
    # =====================================================

    if confirmed_v_shape:
        return {
            "direction": "BUY",
            "setup": "V Shape",
            "level": v_level,
            "level_index": v_index,
            "entry": None,
            "valid": True,
        }

    # =====================================================
    # PRIORITY 4 — CONFIRMED A SHAPE
    # =====================================================

    if confirmed_a_shape:
        return {
            "direction": "SELL",
            "setup": "A Shape",
            "level": a_level,
            "level_index": a_index,
            "entry": None,
            "valid": True,
        }

    # =====================================================
    # NO VALID SETUP
    # =====================================================

    return _invalid_setup()


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "detect_daily_setup",
]