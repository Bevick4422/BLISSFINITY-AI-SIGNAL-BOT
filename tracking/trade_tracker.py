"""
=====================================================
BLISSFINITY SIGNAL
Trade Tracker
Production Version
=====================================================
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =====================================================
# CONFIGURATION
# =====================================================

TRADE_FILE = (
    Path(__file__).resolve().parent / "trades.json"
)


# =====================================================
# TIME
# =====================================================

def _now() -> str:
    """
    Return the current UTC timestamp.
    """

    return datetime.now(timezone.utc).isoformat()


# =====================================================
# FILE OPERATIONS
# =====================================================

def _load_trades() -> list[dict[str, Any]]:
    """
    Load trades from the JSON tracker file.
    """

    if not TRADE_FILE.exists():
        return []

    try:
        data = json.loads(
            TRADE_FILE.read_text(
                encoding="utf-8",
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []

    return data if isinstance(data, list) else []


def _save_trades(
    trades: list[dict[str, Any]],
) -> None:
    """
    Save trades safely using a temporary file.
    """

    TRADE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = TRADE_FILE.with_suffix(".tmp")

    temporary_file.write_text(
        json.dumps(
            trades,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    temporary_file.replace(TRADE_FILE)


def _new_trade_id() -> str:
    """
    Generate a unique trade ID.
    """

    return (
        f"TRADE_{uuid.uuid4().hex[:12].upper()}"
    )


# =====================================================
# STATUS NORMALIZATION
# =====================================================

def _normalise_status(
    trade: dict[str, Any],
) -> str:
    """
    Normalize legacy and current trade statuses.
    """

    status = str(
        trade.get(
            "status",
            trade.get("state", "PENDING"),
        )
    ).upper()

    if status == "CLOSED":
        result = str(
            trade.get("result", "")
        ).upper()

        if result in {
            "WIN",
            "LOSS",
            "BREAKEVEN",
        }:
            return result

    if status in {
        "PENDING",
        "OPEN",
        "WIN",
        "LOSS",
        "BREAKEVEN",
    }:
        return status

    return "PENDING"


# =====================================================
# TRADE RECORDING
# =====================================================

def record_signal(
    signal: dict[str, Any],
) -> str | None:
    """
    Record a new signal unless an active trade already
    exists for the same symbol and direction.
    """

    trades = _load_trades()

    symbol = signal.get("symbol")
    direction = str(
        signal.get("direction", "")
    ).upper()

    if not symbol:
        return None

    if direction not in {
        "BUY",
        "SELL",
    }:
        return None

    for trade in trades:
        same_symbol = (
            trade.get("symbol") == symbol
        )

        same_direction = (
            str(
                trade.get("direction", "")
            ).upper()
            == direction
        )

        status = _normalise_status(trade)

        if (
            same_symbol
            and same_direction
            and status in {
                "PENDING",
                "OPEN",
            }
        ):
            return str(
                trade.get("trade_id")
            )

    trade_id = str(
        signal.get("trade_id")
        or _new_trade_id()
    )

    now = _now()

    trade = {
        "trade_id": trade_id,
        "symbol": symbol,
        "direction": direction,
        "setup": signal.get("setup"),
        "entry": signal.get("entry"),
        "stop_loss": signal.get("stop_loss"),
        "tp1": signal.get("tp1"),
        "tp2": signal.get("tp2"),
        "risk": signal.get("risk"),
        "original_risk": signal.get("risk"),
        "rr": signal.get("rr"),
        "confidence": signal.get("confidence"),

        "status": "PENDING",
        "state": "PENDING",
        "result": None,

        "tp1_hit": False,
        "break_even": False,
        "last_monitored_candle": None,

        # Persistent notification protection.
        "entry_notified": False,
        "tp1_notified": False,
        "tp2_notified": False,
        "stop_loss_notified": False,
        "breakeven_notified": False,

        "opened_at": None,
        "closed_at": None,
        "exit_price": None,
        "result_percent": None,
        "r_multiple": None,

        "created_at": now,
        "updated_at": now,

        "events": [
            {
                "time": now,
                "event": "SIGNAL_RECORDED",
            }
        ],
    }

    trades.append(trade)
    _save_trades(trades)

    return trade_id


# =====================================================
# TRADE QUERIES
# =====================================================

def get_active_trades() -> list[dict[str, Any]]:
    """
    Return all pending and open trades.
    """

    return [
        trade
        for trade in _load_trades()
        if _normalise_status(trade)
        in {
            "PENDING",
            "OPEN",
        }
    ]


def get_all_trades() -> list[dict[str, Any]]:
    """
    Return every recorded trade.
    """

    return _load_trades()


# =====================================================
# EVENT LOGGING
# =====================================================

def _add_event(
    trade: dict[str, Any],
    event: str,
    price: float | None = None,
) -> None:
    """
    Add an event to the trade history.
    """

    events = trade.setdefault(
        "events",
        [],
    )

    event_item: dict[str, Any] = {
        "time": _now(),
        "event": event,
    }

    if price is not None:
        event_item["price"] = price

    events.append(event_item)


# =====================================================
# TRADE CLOSURE
# =====================================================

def _close_trade(
    trade: dict[str, Any],
    result: str,
    exit_price: float,
) -> None:
    """
    Close a trade and calculate its final result.
    """

    entry = float(
        trade["entry"]
    )

    stop_loss = float(
        trade["stop_loss"]
    )

    risk = float(
        trade.get(
            "original_risk",
            abs(entry - stop_loss),
        )
    )

    direction = str(
        trade["direction"]
    ).upper()

    if direction == "BUY":
        result_percent = (
            (exit_price - entry)
            / entry
        ) * 100

        r_multiple = (
            (exit_price - entry)
            / risk
            if risk
            else 0.0
        )

    else:
        result_percent = (
            (entry - exit_price)
            / entry
        ) * 100

        r_multiple = (
            (entry - exit_price)
            / risk
            if risk
            else 0.0
        )

    now = _now()

    trade["status"] = result
    trade["state"] = result
    trade["result"] = result
    trade["closed_at"] = now
    trade["exit_price"] = exit_price
    trade["result_percent"] = round(
        result_percent,
        4,
    )
    trade["r_multiple"] = round(
        r_multiple,
        4,
    )
    trade["updated_at"] = now

    _add_event(
        trade,
        result,
        exit_price,
    )


# =====================================================
# TRADE UPDATE
# =====================================================

def update_trade(
    trade_id: str,
    current_price: float,
    candle_high: float | None = None,
    candle_low: float | None = None,
    candle_timestamp: int | None = None,
) -> dict[str, Any] | None:
    """
    Update one trade.

    The existing current-price behaviour is preserved when
    candle data is not supplied.

    When completed candle high/low values are supplied,
    they allow TP/SL touches to be detected even when
    price has moved away before the next polling cycle.
    """

    trades = _load_trades()

    for trade in trades:
        if trade.get("trade_id") != trade_id:
            continue

        status = _normalise_status(trade)

        if status in {
            "WIN",
            "LOSS",
            "BREAKEVEN",
        }:
            return trade

        entry = float(trade["entry"])
        stop_loss = float(trade["stop_loss"])
        tp1 = float(trade["tp1"])
        tp2 = float(trade["tp2"])

        price = float(current_price)

        direction = str(
            trade["direction"]
        ).upper()

        # -------------------------------------------------
        # Use candle extremes when supplied.
        # Otherwise preserve original ticker behaviour.
        # -------------------------------------------------

        high = (
            float(candle_high)
            if candle_high is not None
            else price
        )

        low = (
            float(candle_low)
            if candle_low is not None
            else price
        )

        # -------------------------------------------------
        # Prevent the same candle being processed twice.
        # -------------------------------------------------

        if candle_timestamp is not None:

            previous_candle = trade.get(
                "last_monitored_candle"
            )

            if previous_candle is not None:

                try:
                    if int(candle_timestamp) <= int(
                        previous_candle
                    ):
                        return trade

                except (TypeError, ValueError):
                    pass

        # -------------------------------------------------
        # PENDING -> OPEN
        # -------------------------------------------------

        if status == "PENDING":

            reached_entry = (
                high >= entry
                if direction == "BUY"
                else low <= entry
            )

            if not reached_entry:

                if candle_timestamp is not None:
                    trade["last_monitored_candle"] = int(
                        candle_timestamp
                    )

                trade["updated_at"] = _now()
                _save_trades(trades)

                return trade

            now = _now()

            trade["status"] = "OPEN"
            trade["state"] = "OPEN"
            trade["opened_at"] = now
            trade["updated_at"] = now

            _add_event(
                trade,
                "ENTRY_REACHED",
                entry,
            )

            # The entry candle is not also used to determine
            # TP/SL because OHLC data cannot establish the
            # intrabar order of those events.

            if candle_timestamp is not None:
                trade["last_monitored_candle"] = int(
                    candle_timestamp
                )

            _save_trades(trades)

            return trade

        # -------------------------------------------------
        # OPEN TRADE MANAGEMENT
        # -------------------------------------------------

        if status == "OPEN":

            if direction == "BUY":

                stopped = low <= stop_loss
                reached_tp1 = high >= tp1
                reached_tp2 = high >= tp2

            else:

                stopped = high >= stop_loss
                reached_tp1 = low <= tp1
                reached_tp2 = low <= tp2

            # -------------------------------------------------
            # If both SL and a target were touched in the same
            # candle, OHLC cannot prove which happened first.
            # Do not invent an outcome.
            # -------------------------------------------------

            if stopped and (
                reached_tp1 or reached_tp2
            ):

                _add_event(
                    trade,
                    "AMBIGUOUS_CANDLE",
                    price,
                )

                if candle_timestamp is not None:
                    trade["last_monitored_candle"] = int(
                        candle_timestamp
                    )

                trade["updated_at"] = _now()
                _save_trades(trades)

                return trade

            # -------------------------------------------------
            # STOP LOSS
            # -------------------------------------------------

            if stopped:

                if trade.get("break_even"):

                    _close_trade(
                        trade,
                        "BREAKEVEN",
                        entry,
                    )

                else:

                    _close_trade(
                        trade,
                        "LOSS",
                        stop_loss,
                    )

            # -------------------------------------------------
            # TP2
            # -------------------------------------------------

            elif reached_tp2:

                _close_trade(
                    trade,
                    "WIN",
                    tp2,
                )

            # -------------------------------------------------
            # TP1 -> MOVE STOP TO ENTRY
            # -------------------------------------------------

            elif (
                reached_tp1
                and not trade.get("tp1_hit")
            ):

                trade["tp1_hit"] = True
                trade["break_even"] = True
                trade["stop_loss"] = entry
                trade["status"] = "OPEN"
                trade["state"] = "BREAK_EVEN"
                trade["updated_at"] = _now()

                _add_event(
                    trade,
                    "TP1_REACHED",
                    tp1,
                )

                _add_event(
                    trade,
                    "STOP_MOVED_TO_ENTRY",
                    entry,
                )

            if candle_timestamp is not None:
                trade["last_monitored_candle"] = int(
                    candle_timestamp
                )

            trade["updated_at"] = _now()

            _save_trades(trades)

            return trade

    return None


# =====================================================
# PERFORMANCE
# =====================================================

def get_performance() -> dict[str, Any]:
    """
    Return current performance statistics.
    """

    trades = _load_trades()

    statuses = [
        _normalise_status(trade)
        for trade in trades
    ]

    total = len(trades)
    pending = statuses.count("PENDING")
    open_trades = (
        statuses.count("OPEN")
        + statuses.count("BREAK_EVEN")
    )

    wins = statuses.count("WIN")
    losses = statuses.count("LOSS")
    breakevens = statuses.count("BREAKEVEN")
    closed = wins + losses + breakevens

    r_values = [
        float(trade["r_multiple"])
        for trade in trades
        if trade.get("r_multiple") is not None
    ]

    return {
        "total_trades": total,
        "pending_trades": pending,
        "open_trades": open_trades,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "closed_trades": closed,
        "active_trades": pending + open_trades,
        "net_r": round(
            sum(r_values),
            4,
        ),
        "win_rate": round(
            (wins / closed) * 100,
            2,
        ) if closed else 0.0,
    }
def claim_notification(trade_id, notification_key):
    """
    Claims a notification exactly once.

    Returns:
        True  - notification has not been sent before
        False - notification was already claimed
    """

    allowed_keys = {
        "entry_notified",
        "tp1_notified",
        "tp2_notified",
        "stop_loss_notified",
        "breakeven_notified",
    }

    if notification_key not in allowed_keys:
        raise ValueError(
            f"Invalid notification key: {notification_key}"
        )

    trades = _load_trades()

    for trade in trades:
        if trade.get("trade_id") != trade_id:
            continue

        # Support older trades created before notification flags existed
        trade.setdefault("entry_notified", False)
        trade.setdefault("tp1_notified", False)
        trade.setdefault("tp2_notified", False)
        trade.setdefault("stop_loss_notified", False)
        trade.setdefault("breakeven_notified", False)

        if trade[notification_key]:
            return False

        trade[notification_key] = True
        _save_trades(trades)

        return True

    return False