"""
BLISSFINITY AI SIGNAL BOT
DAILY MARKET STRUCTURE ENGINE
"""


def detect_daily_structure(df):
    """
    Detect institutional daily market structure.

    Returns:

    HH
    HL
    LH
    LL

    together with overall trend.
    """

    highs = df["high"].tail(10).tolist()
    lows = df["low"].tail(10).tolist()

    last_high = highs[-1]
    previous_high = highs[-2]

    last_low = lows[-1]
    previous_low = lows[-2]

    structure = []

    # =============================
    # HIGHS
    # =============================

    if last_high > previous_high:
        structure.append("HH")
    else:
        structure.append("LH")

    # =============================
    # LOWS
    # =============================

    if last_low > previous_low:
        structure.append("HL")
    else:
        structure.append("LL")

    # =============================
    # TREND
    # =============================

    if "HH" in structure and "HL" in structure:

        trend = "BULLISH"

    elif "LH" in structure and "LL" in structure:

        trend = "BEARISH"

    else:

        trend = "RANGING"

    return {

        "trend": trend,

        "structure": structure,

        "last_high": float(last_high),

        "last_low": float(last_low)

    }