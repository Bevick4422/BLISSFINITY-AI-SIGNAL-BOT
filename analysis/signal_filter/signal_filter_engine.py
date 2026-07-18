"""
BLISSFINITY SIGNAL BOT
SIGNAL FILTER ENGINE
"""

from tracking.trade_manager import add_trade


def approve_signal(
    symbol,
    regime,
    weekly,
    trend,
    confluence,
    rr
):
    """
    Final approval before Telegram.
    """

    # -------------------------
    # Market Regime
    # -------------------------

    if regime["regime"] in [
        "LOW_VOLATILITY",
        "RANGING"
    ]:
        return False, "Bad market regime"

    # -------------------------
    # Weekly Bias
    # -------------------------

    if (
        weekly["bias"] != "NONE"
        and weekly["bias"] != trend["trend"]
    ):
        return False, "Weekly bias conflict"

    # -------------------------
    # Confluence
    # -------------------------

    if confluence["score"] < 90:
        return False, "Confluence below 90"

    # -------------------------
    # Risk Reward
    # -------------------------

    if rr < 2:
        return False, "Risk Reward too low"

    # -------------------------
    # Duplicate Trade
    # -------------------------

    if not add_trade({
        "pair": symbol,
        "side": confluence["signal"]
    }):
        return False, "Duplicate signal"

    return True, "Approved"