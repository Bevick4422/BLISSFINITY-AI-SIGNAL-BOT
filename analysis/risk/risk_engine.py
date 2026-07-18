
"""
BLISSFINITY AI SIGNAL BOT
RISK MANAGEMENT ENGINE
"""


def calculate_risk(entry, atr, direction, rr=3):
    """
    Calculate Entry, Stop Loss, TP1 and TP2.

    TP1 = 1.5R
    TP2 = Full Risk:Reward target
    """

    atr = max(float(atr), 0.0001)

    if direction == "BUY":

        stop_loss = entry - atr

        risk = entry - stop_loss

        tp1 = entry + (risk * 1.5)

        tp2 = entry + (risk * rr)

    else:

        stop_loss = entry + atr

        risk = stop_loss - entry

        tp1 = entry - (risk * 1.5)

        tp2 = entry - (risk * rr)

    return {

        "entry": round(entry, 4),

        "stop_loss": round(stop_loss, 4),

        "tp1": round(tp1, 4),

        "tp2": round(tp2, 4),

        "rr": rr,

    }