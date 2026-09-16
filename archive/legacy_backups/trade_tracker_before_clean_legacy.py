from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =====================================================
# CONFIGURATION
# =====================================================

TRADE_FILE = Path(__file__).resolve().parent / "trades.json"

ACTIVE_STATUSES = {
    "PENDING",
    "OPEN",
}

TERMINAL_STATUSES = {
    "WIN",
    "LOSS",
    "BREAKEVEN",
}


# =====================================================
# TIME HELPERS
# =====================================================

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise_status(trade: dict[str, Any]) -> str:
    status = str(trade.get("status", "PENDING")).upper()

    if status == "BE":
        return "BREAKEVEN"

    return status


# =====================================================
# FILE HELPERS
# =====================================================

def _load_trades() -> list[dict[str, Any]]:
    if not TRADE_FILE.exists():
        return []

    try:
        with TRADE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, OSError):
        return []


def _save_trades(trades: list[dict[str, Any]]) -> None:
    TRADE_FILE.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(
        prefix="trades_",
        suffix=".json",
        dir=str(TRADE_FILE.parent),
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(
                trades,
                f,
                indent=2,
                ensure_ascii=False,
            )

        os.replace(temp_path, TRADE_FILE)

    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


# =====================================================
# EVENT HELPERS
# =====================================================

def _add_event(
    trade: dict[str, Any],
    event: str,
    price: float | None = None,
    timestamp: int | None = None,
) -> None:

    if "events" not in trade:
        trade["events"] = []

    event_data: dict[str, Any] = {
        "event": event,
        "timestamp": _now(),
    }

    if price is not None:
        event_data["price"] = float(price)

    if timestamp is not None:
        event_data["candle_timestamp"] = int(timestamp)

    trade["events"].append(event_data)


# =====================================================
# TRADE CLOSURE
# =====================================================

def _close_trade(
    trade: dict[str, Any],
    status: str,
    exit_price: float,
) -> None:

    now = _now()

    trade["status"] = status
    trade["state"] = status
    trade["exit_price"] = float(exit_price)
    trade["closed_at"] = now
    trade["updated_at"] = now

    if status == "WIN":
        _add_event(
            trade,
            "TP2_REACHED",
            exit_price,
        )

    elif status == "LOSS":
        _add_event(
            trade,
            "STOP_LOSS_HIT",
            exit_price,
        )

    elif status == "BREAKEVEN":
        _add_event(
            trade,
            "BREAKEVEN_EXIT",
            exit_price,
        )


# =====================================================
# RECORD SIGNAL
# =====================================================

def record_signal(
    symbol: str,
    direction: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    tp2: float,
    risk: float | None = None,
    rr: float | None = None,
    confidence: float | None = None,
    signal_time: str | None = None,
    trade_id: str | None = None,
) -> dict[str, Any]:

    trades = _load_trades()

    symbol = str(symbol).upper()
    direction = str(direction).upper()

    # -------------------------------------------------
    # DUPLICATE ACTIVE SYMBOL PROTECTION
    # -------------------------------------------------

    for existing in trades:

        existing_status = _normalise_status(existing)

        if (
            str(existing.get("symbol", "")).upper() == symbol
            and existing_status in ACTIVE_STATUSES
        ):
            return existing

    # -------------------------------------------------
    # CREATE TRADE
    # -------------------------------------------------

    created_at = signal_time or _now()

    trade = {
        "trade_id": trade_id or f"TRADE_{symbol.replace('/', '_')}_{uuid.uuid4().hex[:8]}",
        "symbol": symbol,
        "direction": direction,
        "entry": float(entry),
        "stop_loss": float(stop_loss),
        "tp1": float(tp1),
        "tp2": float(tp2),
        "risk": float(risk) if risk is not None else None,
        "rr": float(rr) if rr is not None else None,
        "confidence": float(confidence) if confidence is not None else None,

        "status": "PENDING",
        "state": "PENDING",

        "created_at": created_at,
        "updated_at": created_at,

        "opened_at": None,
        "closed_at": None,
        "exit_price": None,

        "tp1_hit": False,
        "break_even": False,

        # -------------------------------------------------
        # CANDLE CHECKPOINT
        # -------------------------------------------------
        #
        # Stores the last completed candle processed for
        # this trade. This prevents the same candle from
        # being evaluated repeatedly.
        #
        "last_monitored_candle": None,

        # -------------------------------------------------
        # NOTIFICATION FLAGS
        # -------------------------------------------------

        "entry_notified": False,
        "tp1_notified": False,
        "tp2_notified": False,
        "sl_notified": False,
        "breakeven_notified": False,

        "events": [],
    }

    _add_event(
        trade,
        "SIGNAL_RECORDED",
        entry,
    )

    trades.append(trade)

    _save_trades(trades)

    return trade


# =====================================================
# TRADE RETRIEVAL
# =====================================================

def get_active_trades() -> list[dict[str, Any]]:
    trades = _load_trades()

    return [
        trade
        for trade in trades
        if _normalise_status(trade) in ACTIVE_STATUSES
    ]


def get_all_trades() -> list[dict[str, Any]]:
    return _load_trades()


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

    The tracker can use a completed candle's HIGH/LOW instead
    of relying only on the instantaneous ticker price.

    This prevents missed TP/SL events when price touches a
    level between two polling cycles.

    candle_timestamp is used as a persistent checkpoint so
    the same candle is never processed twice.
    """

    trades = _load_trades()

    for trade in trades:

        if trade.get("trade_id") != trade_id:
            continue

        status = _normalise_status(trade)

        # -------------------------------------------------
        # TERMINAL TRADE
        # -------------------------------------------------

        if status in TERMINAL_STATUSES:
            return trade

        entry = float(trade["entry"])
        stop_loss = float(trade["stop_loss"])
        tp1 = float(trade["tp1"])
        tp2 = float(trade["tp2"])

        price = float(current_price)

        direction = str(
            trade.get("direction", "")
        ).upper()

        # -------------------------------------------------
        # CANDLE RANGE
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
        # DUPLICATE CANDLE PROTECTION
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

                # Even a candle that did not reach entry
                # must be checkpointed so it is not processed
                # repeatedly.

                if candle_timestamp is not None:
                    trade["last_monitored_candle"] = int(
                        candle_timestamp
                    )
                    trade["updated_at"] = _now()
                    _save_trades(trades)

                return trade

            # -------------------------------------------------
            # ENTRY REACHED
            # -------------------------------------------------

            now = _now()

            trade["status"] = "OPEN"
            trade["state"] = "OPEN"
            trade["opened_at"] = now
            trade["updated_at"] = now

            _add_event(
                trade,
                "ENTRY_REACHED",
                entry,
                candle_timestamp,
            )

            # -------------------------------------------------
            # IMPORTANT
            # -------------------------------------------------
            #
            # Do NOT evaluate TP/SL on the same candle that
            # opened the trade.
            #
            # OHLC data cannot reliably tell us whether the
            # entry happened before or after TP/SL inside that
            # candle.
            #
            # The next completed candle will manage the trade.
            # -------------------------------------------------

            if candle_timestamp is not None:
                trade["last_monitored_candle"] = int(
                    candle_timestamp
                )

            trade["updated_at"] = _now()

            _save_trades(trades)

            return trade

        # -------------------------------------------------
        # OPEN TRADE MANAGEMENT
        # -------------------------------------------------

        if status == "OPEN":

            # -------------------------------------------------
            # BUY
            # -------------------------------------------------

            if direction == "BUY":

                stopped = low <= stop_loss
                reached_tp1 = high >= tp1
                reached_tp2 = high >= tp2

            # -------------------------------------------------
            # SELL
            # -------------------------------------------------

            else:

                stopped = high >= stop_loss
                reached_tp1 = low <= tp1
                reached_tp2 = low <= tp2

            # -------------------------------------------------
            # IMPORTANT CANDLE AMBIGUITY CHECK
            # -------------------------------------------------
            #
            # If one candle touches both the protective level
            # and a favorable target, OHLC alone cannot tell
            # which happened first.
            #
            # We do NOT invent an outcome.
            # -------------------------------------------------

            favorable_hit = (
                reached_tp2
                or reached_tp1
            )

            if stopped and favorable_hit:

                _add_event(
                    trade,
                    "AMBIGUOUS_CANDLE",
                    price,
                    candle_timestamp,
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
            # TP1
            # -------------------------------------------------

            elif (
                reached_tp1
                and not trade.get("tp1_hit")
            ):

                trade["tp1_hit"] = True
                trade["break_even"] = True

                # Move SL to entry after TP1.
                trade["stop_loss"] = entry

                trade["status"] = "OPEN"
                trade["state"] = "BREAK_EVEN"
                trade["updated_at"] = _now()

                _add_event(
                    trade,
                    "TP1_REACHED",
                    tp1,
                    candle_timestamp,
                )

                _add_event(
                    trade,
                    "STOP_MOVED_TO_ENTRY",
                    entry,
                    candle_timestamp,
                )

            # -------------------------------------------------
            # SAVE CANDLE CHECKPOINT
            # -------------------------------------------------

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

    trades = _load_trades()

    total = len(trades)

    wins = 0
    losses = 0
    breakevens = 0
    open_trades = 0
    pending_trades = 0

    for trade in trades:

        status = _normalise_status(trade)

        if status == "WIN":
            wins += 1

        elif status == "LOSS":
            losses += 1

        elif status == "BREAKEVEN":
            breakevens += 1

        elif status == "OPEN":
            open_trades += 1

        elif status == "PENDING":
            pending_trades += 1

    closed = wins + losses + breakevens

    win_rate = (
        (wins / closed) * 100
        if closed > 0
        else 0.0
    )

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "open_trades": open_trades,
        "pending_trades": pending_trades,
        "closed_trades": closed,
        "win_rate": round(win_rate, 2),
    }


# =====================================================
# NOTIFICATION CLAIMS
# =====================================================

def claim_notification(
    trade_id: str,
    notification_type: str,
) -> bool:

    trades = _load_trades()

    field_map = {
        "ENTRY": "entry_notified",
        "TP1": "tp1_notified",
        "TP2": "tp2_notified",
        "SL": "sl_notified",
        "BREAKEVEN": "breakeven_notified",
    }

    field = field_map.get(
        str(notification_type).upper()
    )

    if field is None:
        return False

    for trade in trades:

        if trade.get("trade_id") != trade_id:
            continue

        if trade.get(field):
            return False

        trade[field] = True
        trade["updated_at"] = _now()

        _save_trades(trades)

        return True

    return False