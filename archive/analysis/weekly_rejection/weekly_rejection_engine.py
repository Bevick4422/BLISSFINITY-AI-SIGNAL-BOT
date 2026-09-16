
"""
BLISSFINITY AI SIGNAL BOT
WEEKLY REJECTION ENGINE
"""


def detect_weekly_rejection(df, fresh_levels):
    """
    Detect rejection of fresh institutional
    weekly levels.
    """

    latest = df.iloc[-1]

    # ==========================================
    # CHECK FRESH V LEVELS (BUY)
    # ==========================================

    for level in reversed(fresh_levels["fresh_v"]):

        price = level["price"]

        if (
            latest["low"] <= price
            and latest["close"] > price
        ):

            return {

                "rejected": True,

                "direction": "BUY",

                "pattern": "V_SHAPE",

                "level": price,

                "created": level["index"],

                "reason": "Rejected fresh weekly V level"

            }

    # ==========================================
    # CHECK FRESH A LEVELS (SELL)
    # ==========================================

    for level in reversed(fresh_levels["fresh_a"]):

        price = level["price"]

        if (
            latest["high"] >= price
            and latest["close"] < price
        ):

            return {

                "rejected": True,

                "direction": "SELL",

                "pattern": "A_SHAPE",

                "level": price,

                "created": level["index"],

                "reason": "Rejected fresh weekly A level"

            }

    # ==========================================

    return {

        "rejected": False,

        "direction": None,

        "pattern": None,

        "level": None,

        "created": None,

        "reason": "No weekly rejection"

    }