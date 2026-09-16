"""
BLISSFINITY SIGNAL
Risk Engine — Strategy-Aligned

Locked target model:
    TP1 = 2R
    TP2 = 3R

This layer receives the already-selected entry and structural Stop Loss.
It does not discover structure and does not replace the supplied Stop Loss.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


DEFAULT_TP1_RR = 2.0
DEFAULT_TP2_RR = 3.0


def _invalid(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "entry": None,
        "stop_loss": None,
        "risk": None,
        "tp1": None,
        "tp2": None,
        "rr": None,
        "reason": reason,
    }


def build_trade(
    entry: float,
    stop_loss: float,
    direction: str,
    tp1_rr: float = DEFAULT_TP1_RR,
    tp2_rr: float = DEFAULT_TP2_RR,
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
        tp1_rr = float(tp1_rr)
        tp2_rr = float(tp2_rr)
    except (TypeError, ValueError):
        return _invalid("Invalid numeric trade value")

    if entry <= 0 or stop_loss <= 0:
        return _invalid("Entry and Stop Loss must be positive")

    if tp1_rr <= 0 or tp2_rr <= 0:
        return _invalid("Risk/reward values must be positive")

    if tp2_rr <= tp1_rr:
        return _invalid("TP2 R must be greater than TP1 R")

    if direction == "BUY":
        if stop_loss >= entry:
            return _invalid("BUY Stop Loss must be below entry")

        risk = entry - stop_loss
        tp1 = entry + (risk * tp1_rr)
        tp2 = entry + (risk * tp2_rr)

    else:
        if stop_loss <= entry:
            return _invalid("SELL Stop Loss must be above entry")

        risk = stop_loss - entry
        tp1 = entry - (risk * tp1_rr)
        tp2 = entry - (risk * tp2_rr)

    if risk <= 0:
        return _invalid("Invalid non-positive trade risk")

    return {
        "valid": True,
        "entry": entry,
        "stop_loss": stop_loss,
        "risk": risk,
        "tp1": tp1,
        "tp2": tp2,
        "tp1_rr": tp1_rr,
        "tp2_rr": tp2_rr,
        # TP2 is the final target, therefore final trade RR = 3R
        # under the locked defaults.
        "rr": tp2_rr,
        "reason": "Risk built from structural Stop Loss",
        **kwargs,
    }


__all__ = [
    "DEFAULT_TP1_RR",
    "DEFAULT_TP2_RR",
    "build_trade",
]
