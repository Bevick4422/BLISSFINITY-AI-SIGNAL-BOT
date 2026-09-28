"""
=====================================================
BLISSFINITY SIGNAL
Trade Lifecycle Engine
=====================================================

Single-TP lifecycle.

States:

PENDING
   |
   v
OPEN
   |
   +----> BREAK_EVEN
   |          |
   |          +----> CLOSED
   |          |
   |          +----> TP_HIT
   |
   +----> TP_HIT
   |
   +----> STOPPED
              |
              v
            CLOSED
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional


# =====================================================
# TRADE STATES
# =====================================================

PENDING = "PENDING"
OPEN = "OPEN"
BREAK_EVEN = "BREAK_EVEN"
TP_HIT = "TP_HIT"
STOPPED = "STOPPED"
CLOSED = "CLOSED"


# =====================================================
# VALID TRANSITIONS
# =====================================================

VALID_TRANSITIONS = {

    PENDING: {
        OPEN,
    },

    OPEN: {
        BREAK_EVEN,
        TP_HIT,
        STOPPED,
        CLOSED,
    },

    BREAK_EVEN: {
        TP_HIT,
        STOPPED,
        CLOSED,
    },

    TP_HIT: {
        CLOSED,
    },

    STOPPED: {
        CLOSED,
    },

    CLOSED: set(),
}


# =====================================================
# HELPERS
# =====================================================

def _now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


# =====================================================
# CREATE TRADE
# =====================================================

def create_trade(
    signal: Dict,
) -> Dict:

    trade = dict(signal)

    trade.setdefault(
        "state",
        PENDING,
    )

    trade.setdefault(
        "created_at",
        _now(),
    )

    trade.setdefault(
        "opened_at",
        None,
    )

    trade.setdefault(
        "closed_at",
        None,
    )

    trade.setdefault(
        "result",
        None,
    )

    trade.setdefault(
        "exit_price",
        None,
    )

    trade.setdefault(
        "tp_hit",
        False,
    )

    trade.setdefault(
        "break_even",
        False,
    )

    trade.setdefault(
        "stop_loss_hit",
        False,
    )

    return trade


# =====================================================
# VALIDATE TRANSITION
# =====================================================

def can_transition(
    current: str,
    new: str,
) -> bool:

    return new in VALID_TRANSITIONS.get(
        current,
        set(),
    )


# =====================================================
# UPDATE STATE
# =====================================================

def update_state(
    trade: Dict,
    new_state: str,
) -> bool:

    current = trade.get(
        "state",
        PENDING,
    )

    if not can_transition(
        current,
        new_state,
    ):
        return False

    trade["state"] = new_state

    if new_state == OPEN:

        trade["opened_at"] = _now()

    if new_state in (
        CLOSED,
        STOPPED,
    ):

        trade["closed_at"] = _now()

    return True


# =====================================================
# CLOSE TRADE
# =====================================================

def close_trade(
    trade: Dict,
    result: str,
    exit_price: Optional[float],
) -> Dict:

    trade["result"] = result
    trade["exit_price"] = exit_price

    update_state(
        trade,
        CLOSED,
    )

    return trade


# =====================================================
# HELPERS
# =====================================================

def is_active(
    trade: Dict,
) -> bool:

    return trade.get("state") not in (
        CLOSED,
        STOPPED,
    )


def is_closed(
    trade: Dict,
) -> bool:

    return trade.get("state") in (
        CLOSED,
        STOPPED,
    )
