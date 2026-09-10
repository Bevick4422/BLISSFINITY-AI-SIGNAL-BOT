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
    Calculate performance for trades created during
    the current UTC week, Monday through Sunday.

    This function is read-only.
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

    trades = []

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

        if created_time >= week_start:
            trades.append(trade)

    return _calculate_summary(trades)