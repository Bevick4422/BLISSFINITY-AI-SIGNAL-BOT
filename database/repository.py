"""
=====================================================
BLISSFINITY AI SIGNAL BOT
SQLite Repository
=====================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from database.database import get_connection


# =====================================================
# TIME
# =====================================================

def now() -> str:
    return datetime.now(UTC).isoformat()


# =====================================================
# SAVE SIGNAL
# =====================================================

def save_signal(
    symbol: str,
    direction: str,
    setup: str | None,
    entry_type: str |None,
    confidence: int | None,
) -> int:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO signals
        (
            symbol,
            direction,
            setup,
            entry_type,
            confidence,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            direction,
            setup,
            entry_type,
            confidence,
            now(),
        ),
    )

    signal_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return signal_id


# =====================================================
# SAVE TRADE
# =====================================================

def save_trade(trade: dict) -> int:

    conn = get_connection()
    cursor = conn.cursor()

    timestamp = now()

    cursor.execute(
        """
        INSERT INTO trades
        (
            symbol,
            direction,
            entry,
            stop_loss,
            tp1,
            tp2,
            entry_type,
            setup,
            confidence,
            state,
            break_even,
            opened_at,
            closed_at,
            created_at,
            updated_at,
            result,
            rr
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trade["symbol"],
            trade["direction"],
            trade["entry"],
            trade["stop_loss"],
            trade["tp1"],
            trade["tp2"],
            trade.get("entry_type"),
            trade.get("setup"),
            trade.get("confidence"),
            trade.get("state", "PENDING"),
            0,
            None,
            None,
            timestamp,
            timestamp,
            None,
            None,
        ),
    )

    trade_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return trade_id


# =====================================================
# GET TRADE
# =====================================================

def get_trade(trade_id: int) -> dict | None:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE id = ?
        """,
        (trade_id,),
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row) if row else None


# =====================================================
# GET ACTIVE TRADE
# =====================================================

def get_active_trade(
    symbol: str,
    direction: str,
) -> dict | None:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE symbol = ?
        AND direction = ?
        AND state IN ('PENDING','OPEN','TP1_HIT')
        LIMIT 1
        """,
        (
            symbol,
            direction,
        ),
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row) if row else None


# =====================================================
# GET ACTIVE TRADES
# =====================================================

def get_active_trades() -> list[dict]:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE state IN ('PENDING','OPEN','TP1_HIT')
        ORDER BY created_at ASC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =====================================================
# DUPLICATE CHECK
# =====================================================

def trade_exists(
    symbol: str,
    direction: str,
) -> bool:

    return get_active_trade(symbol, direction) is not None


# =====================================================
# UPDATE TRADE
# =====================================================

def update_trade(
    trade_id: int,
    **fields: Any,
) -> bool:

    if not fields:
        return False

    fields["updated_at"] = now()

    conn = get_connection()
    cursor = conn.cursor()

    assignments = ", ".join(
        f"{column} = ?"
        for column in fields.keys()
    )

    values = list(fields.values())
    values.append(trade_id)

    cursor.execute(
        f"""
        UPDATE trades
        SET {assignments}
        WHERE id = ?
        """,
        values,
    )

    success = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return success


# =====================================================
# CLOSE TRADE
# =====================================================

def close_trade(
    trade_id: int,
    result: str,
    rr: float,
) -> bool:

    return update_trade(
        trade_id,
        state="CLOSED",
        result=result,
        rr=rr,
        closed_at=now(),
    )


# =====================================================
# DELETE TRADE
# =====================================================

def delete_trade(trade_id: int) -> bool:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM trades
        WHERE id = ?
        """,
        (trade_id,),
    )

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


# =====================================================
# STATISTICS
# =====================================================

def get_statistics() -> dict:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM statistics
        WHERE id = 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row) if row else {}