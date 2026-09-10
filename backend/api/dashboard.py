"""
=====================================================
BLISSFINITY SIGNAL
Dashboard API
=====================================================
"""

from fastapi import APIRouter

from database.database import get_connection

router = APIRouter()


@router.get("/api/dashboard")
async def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            total_trades,
            open_trades,
            closed_trades,
            wins,
            losses,
            breakevens,
            win_rate,
            total_rr,
            average_rr
        FROM statistics
        WHERE id = 1
        """
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {
            "error": "Statistics not found"
        }

    return dict(row)