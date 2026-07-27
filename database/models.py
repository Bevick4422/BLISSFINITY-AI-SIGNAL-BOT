"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Database Models
=====================================================
"""

from database.database import get_connection


# =====================================================
# CREATE TABLES
# =====================================================

def create_tables() -> None:

    conn = get_connection()

    cursor = conn.cursor()

    # ==================================================
    # TRADES
    # ==================================================

    cursor.execute(
        """
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

            state TEXT NOT NULL,

            break_even INTEGER DEFAULT 0,

            opened_at TEXT,

            closed_at TEXT,

            result TEXT,

            rr REAL,

            created_at TEXT NOT NULL

        )
        """
    )

    # ==================================================
    # SIGNALS
    # ==================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS signals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT NOT NULL,

            direction TEXT NOT NULL,

            setup TEXT,

            entry_type TEXT,

            confidence INTEGER,

            created_at TEXT NOT NULL

        )
        """
    )

    # ==================================================
    # STATISTICS
    # ==================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS statistics (

            id INTEGER PRIMARY KEY CHECK(id = 1),

            total_trades INTEGER DEFAULT 0,

            wins INTEGER DEFAULT 0,

            losses INTEGER DEFAULT 0,

            win_rate REAL DEFAULT 0,

            average_rr REAL DEFAULT 0,

            best_pair TEXT,

            best_entry TEXT

        )
        """
    )

    # Create statistics row if it doesn't exist

    cursor.execute(
        """
        INSERT OR IGNORE INTO statistics (id)
        VALUES (1)
        """
    )

    conn.commit()

    conn.close()