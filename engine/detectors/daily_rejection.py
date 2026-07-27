"""
BLISSFINITY AI SIGNAL BOT
Daily Rejection Detector
"""


def detect_daily_rejection_signal(daily_setup):
    """
    Detect a Daily V Shape or A Shape setup.
    This does NOT generate a signal immediately.
    It returns a setup waiting for H4 BOS confirmation.
    """

    if not daily_setup:
        return None

    if not daily_setup.get("valid"):
        return None

    setup = daily_setup.get("setup")

    if setup == "V Shape":

        return {
            "direction": "BUY",
            "method": "DAILY_REJECTION",
            "status": "WAITING_FOR_BOS",
            "signal": False,
        }

    if setup == "A Shape":

        return {
            "direction": "SELL",
            "method": "DAILY_REJECTION",
            "status": "WAITING_FOR_BOS",
            "signal": False,
        }

    return None