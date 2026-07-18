
"""
BLISSFINITY AI SIGNAL BOT
PERFORMANCE DATABASE
"""

import json
import os
from datetime import datetime

DATABASE_FILE = "tracking/performance/trade_history.json"


def load_history():

    if not os.path.exists(DATABASE_FILE):
        return []

    with open(DATABASE_FILE, "r") as f:

        try:
            return json.load(f)

        except Exception:
            return []


def save_history(history):

    os.makedirs(
        os.path.dirname(DATABASE_FILE),
        exist_ok=True
    )

    with open(DATABASE_FILE, "w") as f:

        json.dump(
            history,
            f,
            indent=4
        )


def save_trade(trade):

    history = load_history()

    trade["closed_at"] = datetime.now().isoformat()

    history.append(trade)

    save_history(history)