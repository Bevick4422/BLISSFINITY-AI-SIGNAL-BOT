"""
BLISSFINITY AI SIGNAL BOT
Production Setup Manager
"""

import json
import os
from datetime import datetime

SETUP_FILE = "data/active_setups.json"


def load_setups():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(SETUP_FILE):
        return []

    try:
        with open(SETUP_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_setups(setups):
    os.makedirs("data", exist_ok=True)

    with open(SETUP_FILE, "w") as f:
        json.dump(setups, f, indent=4)


def get_setup(symbol):
    for setup in load_setups():
        if setup["symbol"] == symbol:
            return setup
    return None


def add_setup(setup):
    setups = load_setups()

    # Prevent duplicate active setups
    for s in setups:
        if s["symbol"] == setup["symbol"]:
            return False

    setup.setdefault("status", "WAITING_FOR_BOS")
    setup.setdefault("bos", False)
    setup.setdefault("signal_sent", False)
    setup.setdefault("created_at", datetime.utcnow().isoformat())

    setups.append(setup)
    save_setups(setups)

    return True


def update_setup(symbol, **kwargs):
    setups = load_setups()

    for setup in setups:
        if setup["symbol"] == symbol:

            setup.update(kwargs)

            save_setups(setups)
            return True

    return False


def remove_setup(symbol):
    setups = [s for s in load_setups() if s["symbol"] != symbol]
    save_setups(setups)