"""
BLISSFINITY SIGNAL
Risk Engine — Strategy-Aligned

Locked target model:
    TP = 2R

This layer receives the already-selected entry and structural Stop Loss.
It does not discover structure and does not replace the supplied Stop Loss.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


DEFAULT_TP_RR = 2.0


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry": None,
        "stop_loss": None,
        "risk": None,
        "tp": None,
        "rr": None,
        "reason": reason,
    }


def build_trade(
    entry: float,
    stop_loss: float,
    direction: str,
    tp_rr: float = DEFAULT_TP_RR,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Build the trade from an explicit structural entry and Stop Loss.

    The supplied stop_loss is authoritative. No fallback stop is generated.
    """
    if direction not in ("BUY", "SELL"):
        return _invalid("Invalid trade direction")

    try:
        entry = float(entry)
        stop_loss = float(stop_loss)
        tp_rr = float(tp_rr)
    except (TypeError, ValueError):
        return _invalid("Invalid numeric trade value")

    if entry <= 0 or stop_loss <= 0:
        return _invalid("Entry and Stop Loss must be positive")

    if tp_rr <= 0:
        return _invalid("Risk/reward value must be positive")

    if direction == "BUY":
        if stop_loss >= entry:
            return _invalid("BUY Stop Loss must be below entry")

        risk = entry - stop_loss
        tp = entry + (risk * tp_rr)

    else:
        if stop_loss <= entry:
            return _invalid("SELL Stop Loss must be above entry")

        risk = stop_loss - entry
        tp = entry - (risk * tp_rr)

    if risk <= 0:
        return _invalid("Invalid non-positive trade risk")

    return {
        "valid": True,
        "entry": entry,
        "stop_loss": stop_loss,
        "risk": risk,
        "tp": tp,
        "tp_rr": tp_rr,
        "rr": tp_rr,
        "reason": "Risk built from structural Stop Loss",
        **kwargs,
    }


__all__ = [
    "DEFAULT_TP_RR",
    "build_trade",
]
