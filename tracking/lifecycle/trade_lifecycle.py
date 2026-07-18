
"""
BLISSFINITY SIGNAL BOT
TRADE LIFECYCLE MANAGER
"""

import json
import os

ACTIVE_FILE = "tracking/active_trades.json"


def load_trades():

    if not os.path.exists(ACTIVE_FILE):
        return []

    with open(ACTIVE_FILE, "r") as f:
        return json.load(f)


def save_trades(trades):

    with open(ACTIVE_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def update_trade(pair, **kwargs):

    trades = load_trades()

    for trade in trades:

        if trade["pair"] == pair:

            trade.update(kwargs)

            break

    save_trades(trades)


def get_trade(pair):

    trades = load_trades()

    for trade in trades:

        if trade["pair"] == pair:
            return trade

    return None