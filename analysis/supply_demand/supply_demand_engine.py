
"""
BLISSFINITY AI SIGNAL BOT
SUPPLY & DEMAND ENGINE
"""

import pandas as pd


def detect_supply_demand(df: pd.DataFrame):
    """
    Detect fresh supply and demand zones.
    """

    recent = df.tail(20)

    demand_low = recent["low"].min()
    demand_high = recent["close"].min()

    supply_low = recent["close"].max()
    supply_high = recent["high"].max()

    current_price = df["close"].iloc[-1]

    in_demand = (
        demand_low <= current_price <= demand_high
    )

    in_supply = (
        supply_low <= current_price <= supply_high
    )

    return {

        "demand_zone": (
            round(demand_low, 4),
            round(demand_high, 4)
        ),

        "supply_zone": (
            round(supply_low, 4),
            round(supply_high, 4)
        ),

        "in_demand": in_demand,

        "in_supply": in_supply

    }