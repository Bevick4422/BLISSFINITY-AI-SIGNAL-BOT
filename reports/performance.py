"""
=====================================================
BLISSFINITY SIGNAL
Performance Engine
=====================================================
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TRADE_FILE = (
    Path(__file__).resolve().parent.parent
    / "tracking"
    / "trades.json"
)


def _load_trades() -> list[dict[str, Any]]:
    """Read trades from the same file used by the live tracker."""

    if not TRADE_FILE.exists():
        return []

    try:
        data = json.loads(
            TRADE_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return []

    return data if isinstance(data, list) else []


def _normalise_status(trade: dict[str, Any]) -> str:
    """Return one consistent trade status."""

    status = str(
        trade.get("status", trade.get("state", "PENDING"))
    ).upper()

    if status == "CLOSED":
        result = str(
            trade.get("result", "")
        ).upper()

        if result in {"WIN", "LOSS", "BREAKEVEN"}:
            return result

    if status in {
        "PENDING",
        "OPEN",
        "BREAK_EVEN",
        "WIN",
        "LOSS",
        "BREAKEVEN",
    }:
        return status

    return "PENDING"


def _is_closed(status: str) -> bool:
    return status in {
        "WIN",
        "LOSS",
        "BREAKEVEN",
    }


def _calculate_summary(
    trades: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate performance from the supplied trades."""

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

    r_values: list[float] = []

    for trade in trades:
        if not _is_closed(
            _normalise_status(trade)
        ):
            continue

        value = trade.get("r_multiple")

        if value is None:
            continue

        try:
            r_values.append(float(value))
        except (TypeError, ValueError):
            continue

    total_rr = round(sum(r_values), 4)

    average_rr = (
        round(total_rr / len(r_values), 4)
        if r_values
        else 0.0
    )

    win_rate = (
        round((wins / closed) * 100, 2)
        if closed
        else 0.0
    )

    return {
        "total": total,
        "pending": pending,
        "open_trades": open_trades,
        "closed_trades": closed,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "win_rate": win_rate,
        "total_rr": total_rr,
        "average_rr": average_rr,
    }


def get_performance_summary() -> dict[str, Any]:
    """
    Calculate overall performance from tracking/trades.json.

    This function is read-only.
    """

    trades = _load_trades()

    return _calculate_summary(trades)


def get_weekly_performance_summary() -> dict[str, Any]:
    """
    Calculate the weekly bot recap for Monday through Saturday.

    Sunday is excluded from the trading window because it is the
    weekly review/report day.

    Closed trades contribute to performance statistics.
    Open and pending trades remain in the trade log but do not
    contribute to closed-book statistics.
    """

    now = datetime.now(timezone.utc)

    week_start = (
        now - timedelta(days=now.weekday())
    ).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    sunday_start = week_start + timedelta(days=6)

    weekly_trades: list[dict[str, Any]] = []

    for trade in _load_trades():
        created_at = trade.get("created_at")

        if not created_at:
            continue

        try:
            created_time = datetime.fromisoformat(
                str(created_at)
            )

            if created_time.tzinfo is None:
                created_time = created_time.replace(
                    tzinfo=timezone.utc
                )

        except ValueError:
            continue

        if (
            created_time >= week_start
            and created_time < sunday_start
        ):
            weekly_trades.append(trade)

    wins = 0
    losses = 0
    breakevens = 0

    gross_wins = 0.0
    gross_losses = 0.0
    net_closed = 0.0

    trade_log: list[dict[str, Any]] = []

    for trade in sorted(
        weekly_trades,
        key=lambda item: str(item.get("created_at", "")),
    ):
        status = _normalise_status(trade)

        r_multiple = trade.get("r_multiple")

        try:
            r_value = float(r_multiple)
        except (TypeError, ValueError):
            r_value = 0.0

        if status == "WIN":
            wins += 1
            gross_wins += r_value
            net_closed += r_value

        elif status == "LOSS":
            losses += 1
            gross_losses += r_value
            net_closed += r_value

        elif status == "BREAKEVEN":
            breakevens += 1

        trade_log.append(
            {
                "created_at": trade.get("created_at"),
                "symbol": trade.get("symbol", "UNKNOWN"),
                "direction": str(
                    trade.get("direction", "")
                ).upper(),
                "status": status,
                "r_multiple": r_value,
            }
        )

    closed_trades = wins + losses + breakevens

    win_rate = (
        round(
            (wins / closed_trades) * 100,
            2,
        )
        if closed_trades
        else 0.0
    )

    return {
        "week_start": week_start,
        "gross_wins": round(gross_wins, 4),
        "gross_losses": round(gross_losses, 4),
        "net_closed": round(net_closed, 4),
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "closed_trades": closed_trades,
        "win_rate": win_rate,
        "trade_log": trade_log,
    }
