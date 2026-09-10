"""
=====================================================
BLISSFINITY SIGNAL 
Trade Monitor
=====================================================

Responsibilities:
- Monitor one trade against the current market price.
- Detect entry activation.
- Detect TP1.
- Move the trade to break-even after TP1.
- Detect TP2 and close the trade as WIN.
- Detect stop-loss and close the trade as LOSS.
- Calculate result percentage and R-multiple.
- TP3 is not used.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# =====================================================
# HELPERS
# =====================================================

def _now() -> str:
    """
    Return the current UTC timestamp.
    """
    return datetime.now(timezone.utc).isoformat()


def _calculate_result(
    direction: str,
    entry: float,
    exit_price: float,
) -> tuple[float, float]:
    """
    Calculate percentage result and R-multiple.

    R is calculated using the original entry-to-stop distance.
    A winning TP2 trade with:
        Entry = 100
        Stop = 90
        TP2 = 130

    returns:
        result_percent = 30.0
        r_multiple = 3.0
    """

    direction = direction.upper()

    if direction == "BUY":
        result_percent = ((exit_price - entry) / entry) * 100
    else:
        result_percent = ((entry - exit_price) / entry) * 100

    return result_percent, 0.0


def _calculate_r_multiple(
    direction: str,
    entry: float,
    stop_loss: float,
    exit_price: float,
) -> float:
    """
    Calculate R-multiple using the original risk distance.
    """

    direction = direction.upper()

    risk_distance = abs(entry - stop_loss)

    if risk_distance == 0:
        return 0.0

    if direction == "BUY":
        reward_distance = exit_price - entry
    else:
        reward_distance = entry - exit_price

    return reward_distance / risk_distance


def _close_trade(
    trade: dict[str, Any],
    result: str,
    exit_price: float,
) -> dict[str, Any]:
    """
    Close a trade and calculate its performance.
    """

    entry = float(trade["entry"])
    stop_loss = float(trade["stop_loss"])
    direction = str(trade["direction"]).upper()

    result_percent, _ = _calculate_result(
        direction=direction,
        entry=entry,
        exit_price=exit_price,
    )

    r_multiple = _calculate_r_multiple(
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        exit_price=exit_price,
    )

    trade["result"] = result
    trade["result_percent"] = round(result_percent, 8)
    trade["r_multiple"] = round(r_multiple, 8)

    trade["status"] = "CLOSED"
    trade["state"] = "CLOSED"

    trade["closed_at"] = _now()

    if result == "WIN":
        trade["tp2_hit"] = True
        trade["last_event"] = "TP2_HIT"

    elif result == "LOSS":
        trade["stop_loss_hit"] = True
        trade["last_event"] = "STOP_LOSS_HIT"

    return trade


# =====================================================
# MAIN MONITOR
# =====================================================

def monitor_trade(
    trade: dict[str, Any],
    current_price: float,
) -> dict[str, Any]:
    """
    Monitor one active trade.

    Supported flow:

    BUY:
        PENDING -> OPEN -> BREAK_EVEN -> CLOSED

    SELL:
        PENDING -> OPEN -> BREAK_EVEN -> CLOSED

    TP1:
        Marks TP1 as hit and moves stop to break-even.

    TP2:
        Closes the trade as WIN.

    Stop-loss:
        Closes the trade as LOSS.

    TP3 is not used.
    """

    if not isinstance(trade, dict):
        raise TypeError("trade must be a dictionary")

    if "direction" not in trade:
        raise ValueError("Trade is missing direction")

    required_fields = (
        "entry",
        "stop_loss",
        "tp1",
        "tp2",
    )

    for field in required_fields:
        if field not in trade:
            raise ValueError(f"Trade is missing required field: {field}")

    direction = str(trade["direction"]).upper()

    if direction not in ("BUY", "SELL"):
        raise ValueError(
            f"Unsupported trade direction: {direction}"
        )

    entry = float(trade["entry"])
    stop_loss = float(trade["stop_loss"])
    tp1 = float(trade["tp1"])
    tp2 = float(trade["tp2"])
    current_price = float(current_price)

    # -------------------------------------------------
    # NORMALIZE EXISTING FIELDS
    # -------------------------------------------------

    trade.setdefault("state", "PENDING")
    trade.setdefault("status", "OPEN")

    trade.setdefault("tp1_hit", False)
    trade.setdefault("tp2_hit", False)
    trade.setdefault("stop_loss_hit", False)

    trade.setdefault("result", None)
    trade.setdefault("result_percent", None)
    trade.setdefault("r_multiple", None)
    trade.setdefault("closed_at", None)

    trade.setdefault("last_event", None)

    # -------------------------------------------------
    # CLOSED TRADES MUST NOT BE PROCESSED AGAIN
    # -------------------------------------------------

    if trade["status"] == "CLOSED":
        return trade

    if trade["state"] == "CLOSED":
        trade["status"] = "CLOSED"
        return trade

    # -------------------------------------------------
    # STOP-LOSS CHECK
    # -------------------------------------------------
    # Stop-loss is checked before targets.
    # This prevents a losing trade from being marked
    # as a winner when the current price is at the SL.

    if direction == "BUY":

        if current_price <= stop_loss:

            return _close_trade(
                trade=trade,
                result="LOSS",
                exit_price=stop_loss,
            )

    else:

        if current_price >= stop_loss:

            return _close_trade(
                trade=trade,
                result="LOSS",
                exit_price=stop_loss,
            )

    # -------------------------------------------------
    # ENTRY CHECK
    # -------------------------------------------------

    if trade["state"] == "PENDING":

        if direction == "BUY":

            if current_price <= entry:
                trade["state"] = "OPEN"
                trade["status"] = "OPEN"
                trade["last_event"] = "ENTRY_HIT"

        else:

            if current_price >= entry:
                trade["state"] = "OPEN"
                trade["status"] = "OPEN"
                trade["last_event"] = "ENTRY_HIT"

    # -------------------------------------------------
    # TP1 CHECK
    # -------------------------------------------------

    if (
        trade["state"] == "OPEN"
        and not trade["tp1_hit"]
    ):

        if direction == "BUY":

            if current_price >= tp1:

                trade["tp1_hit"] = True
                trade["state"] = "BREAK_EVEN"
                trade["status"] = "OPEN"
                trade["break_even"] = entry
                trade["last_event"] = "TP1_HIT"

        else:

            if current_price <= tp1:

                trade["tp1_hit"] = True
                trade["state"] = "BREAK_EVEN"
                trade["status"] = "OPEN"
                trade["break_even"] = entry
                trade["last_event"] = "TP1_HIT"

    # -------------------------------------------------
    # TP2 CHECK
    # -------------------------------------------------

    if (
        trade["state"] == "BREAK_EVEN"
        and trade["tp1_hit"]
        and not trade["tp2_hit"]
    ):

        if direction == "BUY":

            if current_price >= tp2:

                return _close_trade(
                    trade=trade,
                    result="WIN",
                    exit_price=tp2,
                )

        else:

            if current_price <= tp2:

                return _close_trade(
                    trade=trade,
                    result="WIN",
                    exit_price=tp2,
                )

    return trade