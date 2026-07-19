
"""
BLISSFINITY AI SIGNAL BOT
TRADE MANAGER
"""

import json
import os
from datetime import datetime

TRADES_FILE = "tracking/active_trades.json"


# ==========================================
# Ensure Storage Exists
# ==========================================

def ensure_storage():

    os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)

    if not os.path.exists(TRADES_FILE):

        with open(TRADES_FILE, "w") as file:

            json.dump([], file)


# ==========================================
# Load Trades
# ==========================================

def load_trades():

    ensure_storage()

    try:

        with open(TRADES_FILE, "r") as file:

            return json.load(file)

    except Exception as e:

        print(f"Trade File Error: {e}")

        return []


# ==========================================
# Save Trades
# ==========================================

def save_trades(trades):

    ensure_storage()

    with open(TRADES_FILE, "w") as file:

        json.dump(
            trades,
            file,
            indent=4
        )


# ==========================================
# Active Trades
# ==========================================

def get_active_trades():

    return [

        trade

        for trade in load_trades()

        if trade["status"] == "ACTIVE"

    ]


# ==========================================
# Next ID
# ==========================================

def get_next_trade_id():

    trades = load_trades()

    if not trades:

        return 1

    return max(

        trade["id"]

        for trade in trades

    ) + 1


# ==========================================
# Duplicate Protection
# ==========================================

def trade_exists(pair, side):

    for trade in get_active_trades():

        if (

            trade["pair"] == pair

            and

            trade["side"] == side

        ):

            return True

    return False


# ==========================================
# Add Trade
# ==========================================

def add_trade(signal):

    if trade_exists(

        signal["pair"],
        signal["side"]

    ):

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

        "confidence": signal["confidence"],

        "grade": signal["grade"],

        "status": "ACTIVE",

        "entry_hit": False,

        "tp1_hit": False,

        "tp2_hit": False,

        "sl_hit": False,

        "breakeven": False,

        "created_at": datetime.now().isoformat(),

        "closed_at": None

    }

    trades.append(trade)

    save_trades(trades)

    return True


# ==========================================
# Update Trade
# ==========================================

def update_trade(trade_id, **updates):

    trades = load_trades()

    for trade in trades:

        if trade["id"] == trade_id:

            trade.update(updates)

            if trade.get("status") == "CLOSED":

                trade["closed_at"] = datetime.now().isoformat()

            break

    save_trades(trades)


# ==========================================
# Find Trade
# ==========================================

def get_trade(trade_id):

    for trade in load_trades():

        if trade["id"] == trade_id:

            return trade

    return None


# ==========================================
# Remove Closed Trades
# ==========================================

def remove_closed_trades():

    trades = [

        trade

        for trade in load_trades()

        if trade["status"] == "ACTIVE"

    ]

    save_trades(trades)