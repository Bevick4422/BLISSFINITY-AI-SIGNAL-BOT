"""
=====================================================
BLISSFINITY AI SIGNAL BOT
SQLite Database Connection
=====================================================
"""

from pathlib import Path
import sqlite3

# ----------------------------------------------------
# Database Location
# ----------------------------------------------------

DATABASE_FILE = (
    Path(__file__).resolve().parent /
    "blissfinity.db"
)


# ----------------------------------------------------
# Connection
# ----------------------------------------------------

def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection