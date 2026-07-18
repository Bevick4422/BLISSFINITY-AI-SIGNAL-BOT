
"""
BLISSFINITY AI SIGNAL BOT
TRADE MANAGER
"""

import json
import os
from datetime import datetime

TRADES_FILE = "tracking/active_trades.json"


def load_trades():
    if not os.path.exists(TRADES_FILE):
        return []

    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def get_next_trade_id():
    trades = load_trades()

    if not trades:
        return 1

    return max(t["id"] for t in trades) + 1


def trade_exists(pair, side):
    trades = load_trades()

    return any(
        t["pair"] == pair
        and t["side"] == side
        and t["status"] == "ACTIVE"
        for t in trades
    )


def add_trade(signal):
    if trade_exists(signal["pair"], signal["side"]):
        return False

    trades = load_trades()

    trade = {
        "id": get_next_trade_id(),

        "pair": signal["pair"],
        "side": signal["side"],

        "entry": signal["entry"],
        "stop_loss": signal["stop_loss"],

        "tp1": signal["tp1"],
        "tp2": signal["tp2"],

        "rr": signal["rr"],

        "status": "ACTIVE",

        "entry_hit": False,

        "tp1_hit": False,
        "tp2_hit": False,

        "sl_hit": False,

        "breakeven": False,

        "created_at": datetime.now().isoformat()
    }

    trades.append(trade)

    save_trades(trades)

    return True


def get_active_trades():
    trades = load_trades()

    return [
        t for t in trades
        if t["status"] == "ACTIVE"
    ]


def update_trade(trade_id, **updates):
    trades = load_trades()

    for trade in trades:
        if trade["id"] == trade_id:
            trade.update(updates)
            break

    save_trades(trades)