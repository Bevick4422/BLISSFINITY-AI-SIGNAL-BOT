"""
BLISSFINITY AI SIGNAL BOT
MULTI TIMEFRAME CONFIRMATION ENGINE
"""


def confirm_multi_timeframe(
    weekly_bias: str,
    daily_bias: str,
    h4_bias: str
):
    """
    Confirms trend alignment across
    Weekly
    Daily
    4H
    """

    if (
        weekly_bias == "BUY"
        and daily_bias == "BUY"
        and h4_bias == "BUY"
    ):
        return {
            "confirmed": True,
            "direction": "BUY"
        }

    if (
        weekly_bias == "SELL"
        and daily_bias == "SELL"
        and h4_bias == "SELL"
    ):
        return {
            "confirmed": True,
            "direction": "SELL"
        }

    return {
        "confirmed": False,
        "direction": None
    }
