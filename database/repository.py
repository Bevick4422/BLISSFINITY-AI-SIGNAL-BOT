
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
SQLite Repository
Production Version
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
    """
    Current UTC timestamp in ISO format.
    """
    return datetime.now(UTC).isoformat()


# =====================================================
# SIGNALS
# =====================================================

def save_signal(
    symbol: str,
    direction: str,
    setup: str | None,
    entry_type: str | None,
    confidence: int | None,
) -> int:
    """
    Store every generated signal.
    """

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
# TRADES
# =====================================================

def save_trade(trade: dict) -> int:
    """
    Save a newly generated trade.
    """

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
            tp1_hit,
            tp2_hit,
            result,
            rr,
            profit_percent,
            profit_usdt,
            opened_at,
            closed_at,
            duration_minutes,
            created_at,
            updated_at
        )
        VALUES
        (
            ?,?,?,?,?,?,
            ?,?,?,?,
            ?,?,?,?,
            ?,?,?,?,
            ?,?,?,?
        )
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
            "PENDING",
            0,
            0,
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            timestamp,
            timestamp,
        ),
    )

    trade_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return trade_id


# =====================================================
# GET TRADE
# =====================================================

def get_trade(
    trade_id: int,
) -> dict | None:

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

    if row is None:
        return None

    return dict(row)


# =====================================================
# ACTIVE TRADE
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
        AND state IN
        (
            'PENDING',
            'OPEN',
            'TP1_HIT'
        )
        LIMIT 1
        """,
        (
            symbol,
            direction,
        ),
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return dict(row)


# =====================================================
# ALL ACTIVE TRADES
# =====================================================

def get_active_trades() -> list[dict]:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE state IN
        (
            'PENDING',
            'OPEN',
            'TP1_HIT'
        )
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

    return get_active_trade(
        symbol,
        direction,
    ) is not None
# =====================================================
# UPDATE TRADE
# =====================================================

def update_trade(
    trade_id: int,
    **fields: Any,
) -> bool:
    """
    Generic trade updater.
    """

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
# OPEN TRADE
# =====================================================

def open_trade(
    trade_id: int,
) -> bool:
    """
    Trade entry filled.
    """

    return update_trade(
        trade_id,
        state="OPEN",
        opened_at=now(),
    )


# =====================================================
# TP1 HIT
# =====================================================

def mark_tp1_hit(
    trade_id: int,
) -> bool:
    """
    First take profit reached.
    """

    return update_trade(
        trade_id,
        state="TP1_HIT",
        tp1_hit=1,
        break_even=1,
    )


# =====================================================
# MOVE STOP TO BREAKEVEN
# =====================================================

def move_to_break_even(
    trade_id: int,
) -> bool:
    """
    Stop loss moved to entry.
    """

    return update_trade(
        trade_id,
        break_even=1,
    )


# =====================================================
# TP2 HIT
# =====================================================

def mark_tp2_hit(
    trade_id: int,
) -> bool:
    """
    Final target reached.
    """

    return update_trade(
        trade_id,
        state="TP2_HIT",
        tp2_hit=1,
    )


# =====================================================
# CLOSE TRADE
# =====================================================

def close_trade(
    trade_id: int,
    result: str,
    rr: float,
    profit_percent: float = 0.0,
    profit_usdt: float = 0.0,
    duration_minutes: int = 0,
) -> bool:
    """
    Permanently close a trade.
    """

    success = update_trade(
        trade_id,
        state="CLOSED",
        result=result,
        rr=rr,
        profit_percent=profit_percent,
        profit_usdt=profit_usdt,
        duration_minutes=duration_minutes,
        closed_at=now(),
    )

    if success:
        update_statistics()

    return success


# =====================================================
# DELETE TRADE
# =====================================================

def delete_trade(
    trade_id: int,
) -> bool:

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

    if deleted:
        update_statistics()

    return deleted
# =====================================================
# STATISTICS ENGINE
# =====================================================

def update_statistics() -> None:
    """
    Recalculate all performance statistics from the trades table.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------------------------------
    # Trade Counts
    # -------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM trades"
    )
    total_trades = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM trades
        WHERE state IN
        (
            'PENDING',
            'OPEN',
            'TP1_HIT'
        )
        """
    )
    open_trades = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM trades
        WHERE state='CLOSED'
        """
    )
    closed_trades = cursor.fetchone()[0]

    # -------------------------------------------------
    # Results
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM trades
        WHERE result='WIN'
        """
    )
    wins = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM trades
        WHERE result='LOSS'
        """
    )
    losses = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM trades
        WHERE result='BREAKEVEN'
        """
    )
    breakevens = cursor.fetchone()[0]

    # -------------------------------------------------
    # RR
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT COALESCE(SUM(rr),0)
        FROM trades
        WHERE state='CLOSED'
        """
    )
    total_rr = float(cursor.fetchone()[0])

    cursor.execute(
        """
        SELECT COALESCE(AVG(rr),0)
        FROM trades
        WHERE state='CLOSED'
        """
    )
    average_rr = float(cursor.fetchone()[0])

    # -------------------------------------------------
    # Average Duration
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT COALESCE(AVG(duration_minutes),0)
        FROM trades
        WHERE state='CLOSED'
        """
    )
    average_duration = int(cursor.fetchone()[0])

    # -------------------------------------------------
    # Win Rate
    # -------------------------------------------------

    if closed_trades > 0:
        win_rate = round(
            wins / closed_trades * 100,
            2,
        )
    else:
        win_rate = 0.0

    # -------------------------------------------------
    # Win / Loss Streaks
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT result
        FROM trades
        WHERE state='CLOSED'
        ORDER BY closed_at ASC
        """
    )

    history = [
        row[0]
        for row in cursor.fetchall()
    ]

    current_win = 0
    current_loss = 0

    best_win = 0
    best_loss = 0

    temp_win = 0
    temp_loss = 0

    for result in history:

        if result == "WIN":

            temp_win += 1
            temp_loss = 0

            best_win = max(
                best_win,
                temp_win,
            )

            current_win = temp_win
            current_loss = 0

        elif result == "LOSS":

            temp_loss += 1
            temp_win = 0

            best_loss = max(
                best_loss,
                temp_loss,
            )

            current_loss = temp_loss
            current_win = 0

        else:

            temp_win = 0
            temp_loss = 0

            current_win = 0
            current_loss = 0

    # -------------------------------------------------
    # Best Pair
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT symbol,
               COUNT(*) AS wins
        FROM trades
        WHERE result='WIN'
        GROUP BY symbol
        ORDER BY wins DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    best_pair = row[0] if row else None

    # -------------------------------------------------
    # Worst Pair
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT symbol,
               COUNT(*) AS losses
        FROM trades
        WHERE result='LOSS'
        GROUP BY symbol
        ORDER BY losses DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    worst_pair = row[0] if row else None

    # -------------------------------------------------
    # Update Statistics Table
    # -------------------------------------------------

    cursor.execute(
        """
        UPDATE statistics
        SET

            total_trades=?,

            open_trades=?,
            closed_trades=?,

            wins=?,
            losses=?,
            breakevens=?,

            win_rate=?,

            total_rr=?,
            average_rr=?,

            win_streak=?,
            loss_streak=?,

            best_win_streak=?,
            best_loss_streak=?,

            best_pair=?,
            worst_pair=?,

            average_duration=?

        WHERE id=1
        """,
        (
            total_trades,

            open_trades,
            closed_trades,

            wins,
            losses,
            breakevens,

            win_rate,

            total_rr,
            average_rr,

            current_win,
            current_loss,

            best_win,
            best_loss,

            best_pair,
            worst_pair,

            average_duration,
        ),
    )

    conn.commit()
    conn.close()
# =====================================================
# STATISTICS
# =====================================================

def get_statistics() -> dict:
    """
    Return the current statistics row.
    """

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

    if row is None:
        return {}

    return dict(row)


# =====================================================
# DAILY STATISTICS
# =====================================================

def get_daily_statistics() -> dict:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            COUNT(*)                              AS total,
            SUM(result='WIN')                     AS wins,
            SUM(result='LOSS')                    AS losses,
            SUM(result='BREAKEVEN')               AS breakevens,
            COALESCE(SUM(rr),0)                   AS total_rr,
            COALESCE(AVG(rr),0)                   AS average_rr

        FROM trades

        WHERE DATE(created_at)
              = DATE('now')
        """
    )

    row = dict(cursor.fetchone())

    conn.close()

    total = row["total"] or 0

    wins = row["wins"] or 0

    row["win_rate"] = (
        round(wins / total * 100, 2)
        if total
        else 0.0
    )

    return row


# =====================================================
# WEEKLY STATISTICS
# =====================================================

def get_weekly_statistics() -> dict:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            COUNT(*)                              AS total,
            SUM(result='WIN')                     AS wins,
            SUM(result='LOSS')                    AS losses,
            SUM(result='BREAKEVEN')               AS breakevens,
            COALESCE(SUM(rr),0)                   AS total_rr,
            COALESCE(AVG(rr),0)                   AS average_rr

        FROM trades

        WHERE DATE(created_at)
              >= DATE('now','-7 day')
        """
    )

    row = dict(cursor.fetchone())

    conn.close()

    total = row["total"] or 0

    wins = row["wins"] or 0

    row["win_rate"] = (
        round(wins / total * 100, 2)
        if total
        else 0.0
    )

    return row


# =====================================================
# MONTHLY STATISTICS
# =====================================================

def get_monthly_statistics() -> dict:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT

            COUNT(*)                              AS total,
            SUM(result='WIN')                     AS wins,
            SUM(result='LOSS')                    AS losses,
            SUM(result='BREAKEVEN')               AS breakevens,
            COALESCE(SUM(rr),0)                   AS total_rr,
            COALESCE(AVG(rr),0)                   AS average_rr

        FROM trades

        WHERE strftime('%Y-%m', created_at)
              =
              strftime('%Y-%m','now')
        """
    )

    row = dict(cursor.fetchone())

    conn.close()

    total = row["total"] or 0

    wins = row["wins"] or 0

    row["win_rate"] = (
        round(wins / total * 100, 2)
        if total
        else 0.0
    )

    return row


# =====================================================
# TRADE HISTORY
# =====================================================

def get_trade_history(
    limit: int = 100,
) -> list[dict]:
    """
    Return recent trades.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =====================================================
# CLOSED TRADES
# =====================================================

def get_closed_trades() -> list[dict]:

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM trades
        WHERE state='CLOSED'
        ORDER BY closed_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =====================================================
# OPEN TRADES
# =====================================================

def get_open_trades() -> list[dict]:

    return get_active_trades()


# =====================================================
# RESET STATISTICS
# =====================================================

def reset_statistics() -> None:
    """
    Rebuild statistics from the trades table.
    Useful after imports or manual edits.
    """

    update_statistics()


# =====================================================
# INITIALIZE
# =====================================================

# Ensure statistics are synchronized whenever
# the repository module is imported.
