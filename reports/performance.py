"""
=====================================================
BLISSFINITY SIGNAL
Performance Engine
=====================================================
"""

from __future__ import annotations

from database.database import get_connection


def get_performance_summary() -> dict:
    """
    Calculate overall trading performance.

    READ ONLY.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*),
            SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END),
            SUM(CASE WHEN result='LOSS' THEN 1 ELSE 0 END),
            SUM(CASE WHEN result='BREAKEVEN' THEN 1 ELSE 0 END),
            SUM(COALESCE(rr,0)),
            AVG(COALESCE(rr,0))
        FROM trades
        WHERE state='CLOSED'
        """
    )

    row = cursor.fetchone()

    conn.close()

    total = row[0] or 0
    wins = row[1] or 0
    losses = row[2] or 0
    breakevens = row[3] or 0
    total_rr = round(row[4] or 0, 2)
    average_rr = round(row[5] or 0, 2)

    win_rate = round((wins / total) * 100, 2) if total else 0.0

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "breakevens": breakevens,
        "win_rate": win_rate,
        "total_rr": total_rr,
        "average_rr": average_rr,
    }