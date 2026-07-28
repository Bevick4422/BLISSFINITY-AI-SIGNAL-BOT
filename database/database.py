"""
=====================================================
BLISSFINITY AI SIGNAL BOT
SQLite Database Connection
=====================================================
"""

from pathlib import Path
import sqlite3

# =====================================================
# DATABASE LOCATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "blissfinity.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection configured for the bot.
    """

    conn = sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn