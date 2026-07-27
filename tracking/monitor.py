"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Trade Monitor v1
=====================================================
"""

from __future__ import annotations

from typing import Dict

from tracking.lifecycle import (
    OPEN,
    BREAK_EVEN,
    TP1_HIT,
    STOPPED,
    CLOSED,
    update_state,
)


# =====================================================
# CHECK TRADE
# =====================================================

def monitor_trade(
    trade: Dict,
    current_price: float,
) -> Dict:
    """
    Monitor a single active trade.

    Returns the updated trade.
    """

    state = trade.get("state")

    direction = trade["direction"]

    entry = trade["entry"]

    sl = trade["stop_loss"]

    tp1 = trade["tp1"]

    tp2 = trade["tp2"]


    # ==================================================
    # ENTRY
    # ==================================================

    if state == "PENDING":

        if direction == "BUY":

            if current_price <= entry:

                update_state(
                    trade,
                    OPEN,
                )

        else:

            if current_price >= entry:

                update_state(
                    trade,
                    OPEN,
                )


    # ==================================================
    # STOP LOSS
    # ==================================================

    state = trade["state"]

    if state in (
        OPEN,
        BREAK_EVEN,
        TP1_HIT,
    ):

        if direction == "BUY":

            if current_price <= sl:

                update_state(
                    trade,
                    STOPPED,
                )

                return trade

        else:

            if current_price >= sl:

                update_state(
                    trade,
                    STOPPED,
                )

                return trade


    # ==================================================
    # TP1
    # ==================================================

    state = trade["state"]

    if state == OPEN:

        if direction == "BUY":

            if current_price >= tp1:

                update_state(
                    trade,
                    BREAK_EVEN,
                )

        else:

            if current_price <= tp1:

                update_state(
                    trade,
                    BREAK_EVEN,
                )


    # ==================================================
    # TP2
    # ==================================================

    state = trade["state"]

    if state == BREAK_EVEN:

        if direction == "BUY":

            if current_price >= tp2:

                update_state(
                    trade,
                    TP1_HIT,
                )

                update_state(
                    trade,
                    CLOSED,
                )

        else:

            if current_price <= tp2:

                update_state(
                    trade,
                    TP1_HIT,
                )

                update_state(
                    trade,
                    CLOSED,
                )

    return trade