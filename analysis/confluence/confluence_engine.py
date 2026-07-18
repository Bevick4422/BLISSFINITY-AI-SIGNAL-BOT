
"""
BLISSFINITY AI SIGNAL BOT
INSTITUTIONAL CONFLUENCE ENGINE
"""


def calculate_confluence(
    weekly,
    trend,
    structure,
    liquidity,
    supply_demand,
    fvg,
    premium_discount,
    wave,
    momentum
):

    score = 0

    reasons = []

    signal = None

    # ==========================================
    # WEEKLY BIAS (20)
    # ==========================================

    if weekly["bias"] != "NONE":

        score += 20

        reasons.append("Weekly Bias")

    # ==========================================
    # TREND (15)
    # ==========================================

    if trend["trend"] != "RANGING":

        score += 15

        reasons.append("Trend")

    # ==========================================
    # MARKET STRUCTURE (15)
    # ==========================================

    if structure["bos"]:

        score += 15

        reasons.append("Break of Structure")

    # ==========================================
    # LIQUIDITY (15)
    # ==========================================

    if liquidity["grab"] is not None:

        score += 15

        reasons.append("Liquidity Sweep")

    # ==========================================
    # SUPPLY / DEMAND (10)
    # ==========================================

    if (
        supply_demand["in_demand"]
        or
        supply_demand["in_supply"]
    ):

        score += 10

        reasons.append("Supply/Demand")

    # ==========================================
    # FAIR VALUE GAP (10)
    # ==========================================

    if (
        fvg["bullish_fvg"]
        or
        fvg["bearish_fvg"]
    ):

        score += 10

        reasons.append("Fair Value Gap")

    # ==========================================
    # PREMIUM / DISCOUNT (5)
    # ==========================================

    if premium_discount["zone"] != "EQUILIBRIUM":

        score += 5

        reasons.append("Premium/Discount")

    # ==========================================
    # ELLIOTT WAVE (5)
    # ==========================================

    if wave["wave"] in [

        "WAVE_2",

        "WAVE_3"

    ]:

        score += 5

        reasons.append("Wave")

    # ==========================================
    # MOMENTUM (5)
    # ==========================================

    if momentum["momentum"] != "NEUTRAL":

        score += 5

        reasons.append("Momentum")

    # ==========================================
    # SIGNAL
    # ==========================================

    if (
        trend["trend"] == "BULLISH"
        and weekly["bias"] == "BUY"
    ):

        signal = "BUY"

    elif (
        trend["trend"] == "BEARISH"
        and weekly["bias"] == "SELL"
    ):

        signal = "SELL"

    confidence = min(score, 100)

    return {

        "score": score,

        "confidence": confidence,

        "signal": signal,

        "reasons": reasons

    }