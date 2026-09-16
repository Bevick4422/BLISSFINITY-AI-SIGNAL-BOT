"""
=========================================================
BLISSFINITY SIGNAL BOT
Production Signal Builder
=========================================================

Pipeline:

    Valid Entry
        ↓
    ATR
        ↓
    Structure Stop Loss
        ↓
    Risk Engine
        ↓
    Final Signal

This module does NOT detect setups.

It receives an already validated entry and converts it
into a complete standardized trading signal.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from analysis.atr.atr_engine import calculate_atr
from analysis.risk.stoploss_engine import calculate_stop_loss
from engine.risk_engine import build_trade


# =========================================================
# SETTINGS
# =========================================================

DEFAULT_CONFIDENCE = 80.0
ATR_PERIOD = 14


VALID_DIRECTIONS = {
    "BUY",
    "SELL",
}


VALID_ENTRY_TYPES = {
    "LEFT_SHOULDER",
    "BREAK_RETEST",
    "FRESH_LEVEL",
    "ENGULFING",
}


# =========================================================
# TIME
# =========================================================

def _utc_timestamp() -> str:
    """Return the current UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# SAFE FLOAT
# =========================================================

def _to_float(
    value: Any,
) -> Optional[float]:
    """Safely convert a value to float."""

    try:

        if value is None:
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


# =========================================================
# SIGNAL BUILDER
# =========================================================

def build_signal(
    symbol: str,
    direction: str,
    setup: str,
    candle_data,
    entry: float,
    entry_type: str,
    market_data=None,
    stop_loss: Optional[float] = None,
    confidence: float = DEFAULT_CONFIDENCE,
) -> Optional[Dict[str, Any]]:
    """
    Build a complete production trading signal.

    Parameters
    ----------
    symbol:
        Trading symbol.

    direction:
        BUY or SELL.

    setup:
        Daily setup such as V Shape or A Shape.

    candle_data:
        Candle used by the risk engine.

    entry:
        Selected entry price.

    entry_type:
        LEFT_SHOULDER
        BREAK_RETEST
        FRESH_LEVEL
        ENGULFING

    market_data:
        DataFrame used to calculate ATR and structure stop.

    stop_loss:
        Optional externally supplied structure stop.

    confidence:
        Signal confidence score.

    Returns
    -------
    dict | None
        Complete signal or None if validation fails.
    """

    # =====================================================
    # VALIDATE DIRECTION
    # =====================================================

    direction = str(
        direction
    ).upper()

    if direction not in VALID_DIRECTIONS:

        return None

    # =====================================================
    # VALIDATE SYMBOL
    # =====================================================

    if not symbol:

        return None

    # =====================================================
    # VALIDATE SETUP
    # =====================================================

    if not setup:

        return None

    # =====================================================
    # VALIDATE ENTRY TYPE
    # =====================================================

    entry_type = str(
        entry_type
    ).upper()

    if entry_type not in VALID_ENTRY_TYPES:

        return None

    # =====================================================
    # VALIDATE ENTRY
    # =====================================================

    entry = _to_float(entry)

    if entry is None or entry <= 0:

        return None

    # =====================================================
    # VALIDATE CANDLE
    # =====================================================

    if candle_data is None:

        return None

    # =====================================================
    # CALCULATE ATR
    # =====================================================

    atr = None

    if market_data is not None:

        try:

            atr = calculate_atr(
                market_data,
                period=ATR_PERIOD,
            )

        except Exception:

            atr = None

    # =====================================================
    # VALIDATE ATR
    # =====================================================

    atr = _to_float(atr)

    if atr is None or atr <= 0:

        return None

    # =====================================================
    # STRUCTURE STOP LOSS
    # =====================================================

    if stop_loss is None:

        if market_data is None:

            return None

        stop_result = calculate_stop_loss(
            df=market_data,
            atr=atr,
            direction=direction,
            entry_type=entry_type,
        )

        if not isinstance(
            stop_result,
            dict,
        ):

            return None

        if not stop_result.get(
            "valid",
            False,
        ):

            return None

        stop_loss = stop_result.get(
            "stop_loss"
        )

    # =====================================================
    # VALIDATE STOP LOSS
    # =====================================================

    stop_loss = _to_float(
        stop_loss
    )

    if stop_loss is None:

        return None

    # =====================================================
    # STOP LOSS MUST BE ON CORRECT SIDE
    # =====================================================

    if direction == "BUY":

        if stop_loss >= entry:

            return None

    else:

        if stop_loss <= entry:

            return None

    # =====================================================
    # BUILD TRADE
    # =====================================================

    trade = build_trade(
        direction=direction,
        candle=candle_data,
        entry=entry,
        stop_loss=stop_loss,
    )

    if not isinstance(
        trade,
        dict,
    ):

        return None

    if not trade.get(
        "valid",
        False,
    ):

        return None

    # =====================================================
    # EXTRACT TRADE VALUES
    # =====================================================

    final_entry = _to_float(
        trade.get("entry")
    )

    final_stop = _to_float(
        trade.get("stop_loss")
    )

    risk = _to_float(
        trade.get("risk")
    )

    tp1 = _to_float(
        trade.get("tp1")
    )

    tp2 = _to_float(
        trade.get("tp2")
    )



    rr = _to_float(
        trade.get("rr")
    )

    # =====================================================
    # FINAL VALIDATION
    # =====================================================

    if any(
        value is None
        for value in (
            final_entry,
            final_stop,
            risk,
            tp1,
            tp2,
         
            rr,
        )
    ):

        return None

    if risk <= 0:

        return None

    # =====================================================
    # CONFIDENCE
    # =====================================================

    confidence = _to_float(
        confidence
    )

    if confidence is None:

        confidence = DEFAULT_CONFIDENCE

    confidence = max(
        0.0,
        min(
            100.0,
            confidence,
        ),
    )

    # =====================================================
    # FINAL SIGNAL
    # =====================================================

    signal = {

        # -------------------------------------------------
        # IDENTIFICATION
        # -------------------------------------------------

        "symbol": symbol,
        "pair": symbol,

        # -------------------------------------------------
        # DIRECTION
        # -------------------------------------------------

        "direction": direction,
        "side": direction,

        # -------------------------------------------------
        # STRATEGY
        # -------------------------------------------------

        "setup": setup,
        "entry_type": entry_type,

        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        "entry": round(
            final_entry,
            8,
        ),

        "stop_loss": round(
            final_stop,
            8,
        ),

        # -------------------------------------------------
        # RISK
        # -------------------------------------------------

        "risk": round(
            risk,
            8,
        ),

        "atr": round(
            atr,
            8,
        ),

        # -------------------------------------------------
        # TARGETS
        # -------------------------------------------------

        "tp1": round(
            tp1,
            8,
        ),

        "tp2": round(
            tp2,
            8,
        ),

        # -------------------------------------------------
        # REWARD / RISK
        # -------------------------------------------------

        "rr": round(
            rr,
            4,
        ),

        # -------------------------------------------------
        # CONFIDENCE
        # -------------------------------------------------

        "confidence": round(
            confidence,
            2,
        ),

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        "status": "OPEN",
        "valid": True,

        # -------------------------------------------------
        # TIMESTAMP
        # -------------------------------------------------

        "created_at": _utc_timestamp(),

    }

    return signal


# =========================================================
# VALIDATE SIGNAL
# =========================================================

def validate_signal(
    signal: Dict[str, Any],
) -> bool:
    """
    Validate a completed signal.
    """

    if not isinstance(
        signal,
        dict,
    ):

        return False

    if signal.get(
        "valid"
    ) is not True:

        return False

    direction = signal.get(
        "direction"
    )

    if direction not in VALID_DIRECTIONS:

        return False

    required = (
        "symbol",
        "setup",
        "entry_type",
        "entry",
        "stop_loss",
        "risk",
        "tp1",
        "tp2",
   
        "rr",
        "confidence",
    )

    for key in required:

        if signal.get(key) is None:

            return False

    entry = _to_float(
        signal.get("entry")
    )

    stop_loss = _to_float(
        signal.get("stop_loss")
    )

    if entry is None or stop_loss is None:

        return False

    if direction == "BUY":

        if stop_loss >= entry:

            return False

    else:

        if stop_loss <= entry:

            return False

    return True


# =========================================================
# FORMAT SIGNAL
# =========================================================

def format_signal(
    signal: Dict[str, Any],
) -> str:
    """
    Convert a valid signal into a Telegram-ready message.
    """

    if not validate_signal(
        signal
    ):

        return "INVALID SIGNAL"

    return (
        "🚨 BLISSFINITY SIGNAL\n"
        "\n"
        f"Symbol: {signal['symbol']}\n"
        f"Direction: {signal['direction']}\n"
        f"Setup: {signal['setup']}\n"
        f"Entry Type: {signal['entry_type']}\n"
        "\n"
        f"Entry: {signal['entry']}\n"
        f"Stop Loss: {signal['stop_loss']}\n"
        f"TP1: {signal['tp1']}\n"
        f"TP2: {signal['tp2']}\n"
       
        f"Risk: {signal['risk']}\n"
        f"RR: {signal['rr']:.2f}R\n"
        f"Confidence: {signal['confidence']:.0f}%"
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "build_signal",
    "validate_signal",
    "format_signal",
]