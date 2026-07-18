"""
BLISSFINITY AI SIGNAL BOT
ANALYTICS ENGINE
"""

from tracking.performance.performance_database import load_history


def calculate_statistics():

    history = load_history()

    if not history:

        return {
            "total": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0,
            "average_rr": 0
        }

    total = len(history)

    wins = sum(
        1 for t in history
        if t["result"] == "WIN"
    )

    losses = sum(
        1 for t in history
        if t["result"] == "LOSS"
    )

    average_rr = sum(
        t["rr"] for t in history
    ) / total

    return {

        "total": total,

        "wins": wins,

        "losses": losses,

        "win_rate": round(
            wins / total * 100,
            2
        ),

        "average_rr": round(
            average_rr,
            2
        )

    }