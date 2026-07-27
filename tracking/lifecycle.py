"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Trade Lifecycle Engine v1
=====================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional


# =====================================================
# TRADE STATES
# =====================================================

PENDING = "PENDING"
OPEN = "OPEN"
BREAK_EVEN = "BREAK_EVEN"
TP1_HIT = "TP1_HIT"
TP2_HIT = "TP2_HIT"
STOPPED = "STOPPED"
CLOSED = "CLOSED"


VALID_TRANSITIONS = {

    PENDING: {
        OPEN,
    },

    OPEN: {
        BREAK_EVEN,
        STOPPED,
        CLOSED,
    },

    BREAK_EVEN: {
        TP1_HIT,
        STOPPED,
        CLOSED,
    },

    TP1_HIT: {
        TP2_HIT,
        STOPPED,
        CLOSED,
    },

    TP2_HIT: {
        CLOSED,
    },

    STOPPED: {
        CLOSED,
    },

    CLOSED: set(),
}


# =====================================================
# CREATE TRADE
# =====================================================

def create_trade(signal: Dict) -> Dict:

    trade = dict(signal)

    trade.setdefault("state", PENDING)

    trade.setdefault(
        "created_at",
        datetime.utcnow().isoformat(),
    )

    trade.setdefault("opened_at", None)
    trade.setdefault("closed_at", None)

    trade.setdefault("result", None)

    trade.setdefault("exit_price", None)

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

        trade["opened_at"] = (
            datetime.utcnow().isoformat()
        )

    if new_state in (
        CLOSED,
        STOPPED,
    ):

        trade["closed_at"] = (
            datetime.utcnow().isoformat()
        )

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