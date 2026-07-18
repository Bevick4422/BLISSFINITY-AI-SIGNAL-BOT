"""
BLISSFINITY AI SIGNAL BOT
WEEKLY KEY LEVEL ENGINE
"""


def detect_weekly_key_levels(df):
    """
    Detect institutional A-Shape and V-Shape
    weekly key levels.

    Returns the latest confirmed levels.
    """

    a_levels = []
    v_levels = []

    candles = len(df)

    for i in range(1, candles):

        previous = df.iloc[i - 1]
        current = df.iloc[i]

        # -------------------------
        # V SHAPE
        # Bearish -> Bullish
        # -------------------------

        if (
            previous["close"] < previous["open"]
            and
            current["close"] > current["open"]
        ):

            v_levels.append({

                "type": "V",

                "price": float(previous["low"]),

                "index": i - 1

            })

        # -------------------------
        # A SHAPE
        # Bullish -> Bearish
        # -------------------------

        elif (

            previous["close"] > previous["open"]

            and

            current["close"] < current["open"]

        ):

            a_levels.append({

                "type": "A",

                "price": float(previous["high"]),

                "index": i - 1

            })

    latest_v = v_levels[-1] if v_levels else None

    latest_a = a_levels[-1] if a_levels else None

    return {

        "latest_v": latest_v,

        "latest_a": latest_a,

        "all_v": v_levels,

        "all_a": a_levels

    }