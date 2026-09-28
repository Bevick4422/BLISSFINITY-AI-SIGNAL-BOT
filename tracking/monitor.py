"""
=====================================================
BLISSFINITY SIGNAL
Trade Monitor
=====================================================

Single-TP lifecycle.

Rules:
- One TP only.
- TP is 2R.
- TP touched -> WIN.
- SL hit before protection -> LOSS.
- Protection means the stop has been moved to entry.
- Protected trade returning to entry -> BREAKEVEN = 0R.
- Protected trade reaching TP -> WIN.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# =====================================================
# HELPERS
# =====================================================

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _calculate_result(
    direction: str,
    entry: float,
    exit_price: float,
) -> tuple[float, float]:

    direction = direction.upper()

    if direction == "BUY":
        result_percent = (
            (exit_price - entry) / entry
        ) * 100
    else:
        result_percent = (
            (entry - exit_price) / entry
        ) * 100

    return result_percent, 0.0


def _calculate_r_multiple(
    direction: str,
    entry: float,
    original_stop_loss: float,
    exit_price: float,
) -> float:

    direction = direction.upper()

    risk_distance = abs(
        entry - original_stop_loss
    )

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

    entry = float(trade["entry"])

    original_stop_loss = float(
        trade.get(
            "original_stop_loss",
            trade["stop_loss"],
        )
    )

    direction = str(
        trade["direction"]
    ).upper()

    result_percent, _ = _calculate_result(
        direction=direction,
        entry=entry,
        exit_price=exit_price,
    )

    r_multiple = _calculate_r_multiple(
        direction=direction,
        entry=entry,
        original_stop_loss=original_stop_loss,
        exit_price=exit_price,
    )

    trade["result"] = result
    trade["result_percent"] = round(
        result_percent,
        8,
    )
    trade["r_multiple"] = round(
        r_multiple,
        8,
    )

    trade["exit_price"] = exit_price
    trade["status"] = "CLOSED"
    trade["state"] = "CLOSED"
    trade["closed_at"] = _now()

    if result == "WIN":
        trade["tp_hit"] = True
        trade["last_event"] = "TP_HIT"

    elif result == "LOSS":
        trade["stop_loss_hit"] = True
        trade["last_event"] = "STOP_LOSS_HIT"

    elif result == "BREAKEVEN":
        trade["break_even"] = True
        trade["last_event"] = "BREAKEVEN_HIT"

    return trade


# =====================================================
# MAIN MONITOR
# =====================================================

def monitor_trade(
    trade: dict[str, Any],
    current_price: float,
) -> dict[str, Any]:

    if not isinstance(trade, dict):
        raise TypeError(
            "trade must be a dictionary"
        )

    if "direction" not in trade:
        raise ValueError(
            "Trade is missing direction"
        )

    required_fields = (
        "entry",
        "stop_loss",
        "tp",
    )

    for field in required_fields:
        if field not in trade:
            raise ValueError(
                f"Trade is missing required field: {field}"
            )

    direction = str(
        trade["direction"]
    ).upper()

    if direction not in ("BUY", "SELL"):
        raise ValueError(
            f"Unsupported trade direction: {direction}"
        )

    entry = float(trade["entry"])
    stop_loss = float(trade["stop_loss"])
    tp = float(trade["tp"])
    current_price = float(current_price)

    # -------------------------------------------------
    # NORMALIZE
    # -------------------------------------------------

    trade.setdefault(
        "state",
        "PENDING",
    )

    trade.setdefault(
        "status",
        "OPEN",
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

    trade.setdefault(
        "result",
        None,
    )

    trade.setdefault(
        "result_percent",
        None,
    )

    trade.setdefault(
        "r_multiple",
        None,
    )

    trade.setdefault(
        "exit_price",
        None,
    )

    trade.setdefault(
        "closed_at",
        None,
    )

    trade.setdefault(
        "last_event",
        None,
    )

    # Preserve original risk.
    trade.setdefault(
        "original_stop_loss",
        stop_loss,
    )

    # -------------------------------------------------
    # CLOSED TRADES
    # -------------------------------------------------

    if trade["status"] == "CLOSED":
        return trade

    if trade["state"] == "CLOSED":
        trade["status"] = "CLOSED"
        return trade

    # -------------------------------------------------
    # ENTRY
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
    # TP CHECK
    # -------------------------------------------------
    #
    # If TP is actually touched:
    # WIN.
    #
    # This remains true even after protection.
    # -------------------------------------------------

    if not trade["tp_hit"]:

        if direction == "BUY":

            if current_price >= tp:

                return _close_trade(
                    trade=trade,
                    result="WIN",
                    exit_price=tp,
                )

        else:

            if current_price <= tp:

                return _close_trade(
                    trade=trade,
                    result="WIN",
                    exit_price=tp,
                )

    # -------------------------------------------------
    # PROTECTED TRADE
    # -------------------------------------------------
    #
    # Protection is activated by the existing trade
    # management layer.
    #
    # Once state == BREAK_EVEN:
    #
    #   TP touched     -> WIN
    #   return entry   -> BREAKEVEN
    #
    # No TP threshold is invented here.
    # -------------------------------------------------

    if (
        trade["state"] == "BREAK_EVEN"
        and trade.get("break_even") is True
    ):

        if direction == "BUY":

            if current_price <= entry:

                return _close_trade(
                    trade=trade,
                    result="BREAKEVEN",
                    exit_price=entry,
                )

        else:

            if current_price >= entry:

                return _close_trade(
                    trade=trade,
                    result="BREAKEVEN",
                    exit_price=entry,
                )

        return trade

    # -------------------------------------------------
    # NORMAL STOP LOSS
    # -------------------------------------------------
    #
    # Only applies before protection.
    # -------------------------------------------------

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

    return trade
