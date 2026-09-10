def calculate_risk(entry, atr, direction, rr=3):
    """
    Calculate entry, stop-loss, and take-profit levels
    using ATR-based risk management.
    """
    entry = float(entry)
    atr = max(float(atr), 0.0001)
    rr = float(rr)

    if direction == "BUY":
        stop_loss = entry - atr
        risk = entry - stop_loss
        tp1 = entry + (risk * 1.5)
        tp2 = entry + (risk * rr)

    elif direction == "SELL":
        stop_loss = entry + atr
        risk = stop_loss - entry
        tp1 = entry - (risk * 1.5)
        tp2 = entry - (risk * rr)

    else:
        raise ValueError("Direction must be BUY or SELL")

    return {
        "entry": round(entry, 4),
        "stop_loss": round(stop_loss, 4),
        "tp1": round(tp1, 4),
        "tp2": round(tp2, 4),
        "rr": rr,
    }


def calculate_trade(entry, atr, direction, rr=3):
    """
    Compatibility function used by the trade-management tests.
    """
    result = calculate_risk(
        entry=entry,
        atr=atr,
        direction=direction,
        rr=rr,
    )

    return {
        **result,
        "take_profit": result["tp2"],
    }


__all__ = [
    "calculate_risk",
    "calculate_trade",
]