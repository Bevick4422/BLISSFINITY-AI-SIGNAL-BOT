"""
BLISSFINITY Smart Risk Manager
Calculates dynamic SL, TP1, TP2 and RR.
"""


def build_trade(
    direction,
    entry,
    structure_high,
    structure_low,
    demand_zone=None,
    supply_zone=None,
):

    if direction == "BUY":

        if demand_zone is not None:
            stop = demand_zone * 0.998
        else:
            stop = structure_low * 0.998

        risk = entry - stop

        tp1 = entry + (risk * 3)
        tp2 = entry + (risk * 5)

    else:

        if supply_zone is not None:
            stop = supply_zone * 1.002
        else:
            stop = structure_high * 1.002

        risk = stop - entry

        tp1 = entry - (risk * 3)
        tp2 = entry - (risk * 5)

    rr = round(abs(tp2 - entry) / abs(entry - stop), 2)

    return {
        "entry": round(entry, 4),
        "stop": round(stop, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "rr": rr,
    }


def apply_smart_risk(signal):
    """
    Takes the raw AI signal and adds SL/TP.
    """

    if signal is None:
        return None

    trade = build_trade(
        direction=signal["direction"],
        entry=signal["entry"],
        structure_high=signal["market_structure"].get(
            "recent_high",
            signal["entry"] * 1.01,
        ),
        structure_low=signal["market_structure"].get(
            "recent_low",
            signal["entry"] * 0.99,
        ),
        demand_zone=signal["supply_demand"].get("demand"),
        supply_zone=signal["supply_demand"].get("supply"),
    )

    signal.update(trade)

    return signal
