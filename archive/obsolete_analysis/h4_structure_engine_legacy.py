"""
BLISSFINITY AI SIGNAL BOT
4H MARKET STRUCTURE ENGINE
"""


def detect_h4_structure(df):
    """
    Detect 4H institutional market structure.
    """

    highs = df["high"].tail(10).tolist()
    lows = df["low"].tail(10).tolist()

    current_high = highs[-1]
    previous_high = highs[-2]

    current_low = lows[-1]
    previous_low = lows[-2]

    structure = []

    # -----------------------------
    # Highs
    # -----------------------------

    if current_high > previous_high:
        structure.append("HH")
    else:
        structure.append("LH")

    # -----------------------------
    # Lows
    # -----------------------------

    if current_low > previous_low:
        structure.append("HL")
    else:
        structure.append("LL")

    # -----------------------------
    # Trend
    # -----------------------------

    if structure == ["HH", "HL"]:
        trend = "BULLISH"

    elif structure == ["LH", "LL"]:
        trend = "BEARISH"

    else:
        trend = "RANGING"

    return {

        "trend": trend,

        "structure": structure,

        "current_high": float(current_high),

        "current_low": float(current_low)

    }