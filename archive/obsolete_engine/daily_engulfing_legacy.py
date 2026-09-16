"""
BLISSFINITY AI SIGNAL BOT
Daily Engulfing Detector
"""


def detect_daily_engulfing_signal(daily_setup):
    """
    Generate an immediate signal from a Daily Engulfing setup.
    """

    if not daily_setup:
        return None

    if not daily_setup.get("valid"):
        return None

    setup = daily_setup.get("setup")

    if setup == "Bullish Engulfing":

        return {
            "direction": "BUY",
            "method": "DAILY_ENGULFING",
            "status": "READY",
            "signal": True,
        }

    if setup == "Bearish Engulfing":

        return {
            "direction": "SELL",
            "method": "DAILY_ENGULFING",
            "status": "READY",
            "signal": True,
        }

    return None