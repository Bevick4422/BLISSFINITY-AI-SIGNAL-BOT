"""
BLISSFINITY Risk Manager
"""


def build_trade(direction, entry):

    if direction == "BUY":

        stop = entry * 0.995

        tp1 = entry * 1.010

        tp2 = entry * 1.025

    else:

        stop = entry * 1.005

        tp1 = entry * 0.990

        tp2 = entry * 0.975

    rr = round(abs(tp2 - entry) / abs(entry - stop), 2)

    return {

        "entry": round(entry, 4),

        "stop": round(stop, 4),

        "tp1": round(tp1, 4),

        "tp2": round(tp2, 4),

        "rr": rr,

    }
