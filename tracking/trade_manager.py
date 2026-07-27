
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
# REQUIRED FIELDS
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

    for field in REQUIRED_FIELDS:

        if field not in signal:

            return False, f"Missing required field: {field}"

    return True, ""


# =====================================================
# ADD TRADE
# =====================================================

def add_trade(signal: dict[str, Any]) -> int | None:

    valid, message = validate_signal(signal)

    if not valid:

        print(message)
        return None

    symbol = signal["symbol"]
    direction = signal["direction"]

    if trade_exists(symbol, direction):

        print(f"{symbol} | Duplicate active trade")

        return None

    signal.setdefault("state", "PENDING")
    signal.setdefault("entry_type", "ENGULFING")
    signal.setdefault("confidence", 80)
    signal.setdefault("setup", None)

    trade_id = save_trade(signal)

    return trade_id