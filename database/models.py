"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Database Models
=====================================================
"""

from database.database import get_connection


def create_tables() -> None:
    """
    Create all required database tables.
    Safe to call every time the bot starts.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # TRADES
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,

        entry REAL NOT NULL,
        stop_loss REAL NOT NULL,

        tp1 REAL NOT NULL,
        tp2 REAL NOT NULL,

        entry_type TEXT,
        setup TEXT,
        confidence INTEGER,

        state TEXT NOT NULL DEFAULT 'PENDING',

        break_even INTEGER NOT NULL DEFAULT 0,

        tp1_hit INTEGER NOT NULL DEFAULT 0,
        tp2_hit INTEGER NOT NULL DEFAULT 0,

        result TEXT,

        rr REAL,
        profit_percent REAL,
        profit_usdt REAL,

        opened_at TEXT,
        closed_at TEXT,
        duration_minutes INTEGER,

        created_at TEXT NOT NULL,
        updated_at TEXT

    )
    """)

    # =====================================================
    # SIGNALS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,

        setup TEXT,
        entry_type TEXT,
        confidence INTEGER,

        created_at TEXT NOT NULL

    )
    """)

    # =====================================================
    # STATISTICS
    # =====================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS statistics (

        id INTEGER PRIMARY KEY CHECK(id = 1),

        total_trades INTEGER NOT NULL DEFAULT 0,

        open_trades INTEGER NOT NULL DEFAULT 0,
        closed_trades INTEGER NOT NULL DEFAULT 0,

        wins INTEGER NOT NULL DEFAULT 0,
        losses INTEGER NOT NULL DEFAULT 0,
        breakevens INTEGER NOT NULL DEFAULT 0,

        win_rate REAL NOT NULL DEFAULT 0,

        total_rr REAL NOT NULL DEFAULT 0,
        average_rr REAL NOT NULL DEFAULT 0,

        win_streak INTEGER NOT NULL DEFAULT 0,
        loss_streak INTEGER NOT NULL DEFAULT 0,

        best_win_streak INTEGER NOT NULL DEFAULT 0,
        best_loss_streak INTEGER NOT NULL DEFAULT 0,

        best_pair TEXT,
        worst_pair TEXT,

        average_duration INTEGER DEFAULT 0

    )
    """)

    # =====================================================
    # DEFAULT STATISTICS ROW
    # =====================================================

    cursor.execute("""
    INSERT OR IGNORE INTO statistics (id)
    VALUES (1)
    """)

    conn.commit()
    conn.close()