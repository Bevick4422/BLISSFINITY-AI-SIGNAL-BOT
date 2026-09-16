"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Trade Manager
=====================================================
"""

from __future__ import annotations

from typing import Any

from database.repository import (
    save_trade,
    trade_exists,
)


# =====================================================
# REQUIRED SIGNAL FIELDS
# =====================================================

REQUIRED_FIELDS = (
    "symbol",
    "direction",
    "entry",
    "stop_loss",
    "tp1",
    "tp2",
)


# =====================================================
# VALIDATE SIGNAL
# =====================================================

def validate_signal(signal: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate required trade fields.
    """

    for field in REQUIRED_FIELDS:

        if field not in signal:
            return False, f"Missing required field: {field}"

        if signal[field] is None:
            return False, f"{field} cannot be None"

    return True, ""


# =====================================================
# ADD TRADE
# =====================================================

def add_trade(signal: dict[str, Any]) -> int | None:
    """
    Save a new trade if no active duplicate exists.
    """

    valid, message = validate_signal(signal)

    if not valid:
        print(f"Trade Validation Error | {message}")
        return None

    symbol = signal["symbol"]
    direction = signal["direction"]

    if trade_exists(symbol, direction):
        print(f"{symbol} | Active trade already exists.")
        return None

    trade = signal.copy()

    trade.setdefault("state", "PENDING")
    trade.setdefault("entry_type", "ENGULFING")
    trade.setdefault("setup", None)
    trade.setdefault("confidence", 80)
    trade.setdefault("break_even", 0)

    return save_trade(trade)