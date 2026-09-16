
"""
BLISSFINITY AI SIGNAL BOT
PREMIUM / DISCOUNT ENGINE
"""

import pandas as pd


def detect_premium_discount(df: pd.DataFrame):
    """
    Determine whether price is trading
    in Premium, Discount or Equilibrium.
    """

    swing_high = df["high"].tail(50).max()
    swing_low = df["low"].tail(50).min()

    equilibrium = (swing_high + swing_low) / 2

    current_price = df["close"].iloc[-1]

    if current_price > equilibrium:

        zone = "PREMIUM"

    elif current_price < equilibrium:

        zone = "DISCOUNT"

    else:

        zone = "EQUILIBRIUM"

    return {

        "zone": zone,

        "current_price": round(current_price, 4),

        "equilibrium": round(equilibrium, 4),

        "premium": round(swing_high, 4),

        "discount": round(swing_low, 4)

    }