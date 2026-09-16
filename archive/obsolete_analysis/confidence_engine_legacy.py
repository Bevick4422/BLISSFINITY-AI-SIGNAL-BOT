
"""
BLISSFINITY AI SIGNAL BOT
CONFIDENCE ENGINE

Purpose:
Calculate the quality of an already approved trade.

This engine NEVER approves or rejects trades.
It only assigns a confidence score and grade.
"""


def calculate_confidence(
    weekly,
    daily_structure,
    daily_bos,
    h4_structure,
    h4_bos,
    liquidity,
    entry,
    risk,
):
    score = 0
    reasons = []

    # =====================================
    # WEEKLY BIAS
    # =====================================

    if weekly["bias"] != "NONE":
        score += 20
        reasons.append("Weekly Bias")

    # =====================================
    # DAILY STRUCTURE
    # =====================================

    if daily_structure["trend"] != "RANGING":
        score += 15
        reasons.append("Daily Structure")

    # =====================================
    # DAILY BOS
    # =====================================

    if daily_bos["bos"]:
        score += 15
        reasons.append("Daily BOS")

    # =====================================
    # H4 STRUCTURE
    # =====================================

    if h4_structure["trend"] != "RANGING":
        score += 10
        reasons.append("H4 Structure")

    # =====================================
    # H4 BOS
    # =====================================

    if h4_bos["bos"]:
        score += 10
        reasons.append("H4 BOS")

    # =====================================
    # LIQUIDITY
    # =====================================

    if liquidity["liquidity_grab"]:
        score += 10
        reasons.append("Liquidity Sweep")

    # =====================================
    # ENTRY
    # =====================================

    if entry["approved"]:
        score += 10
        reasons.append("Entry Trigger")

    # =====================================
    # RISK
    # =====================================

    if risk["rr"] >= 3:
        score += 10
        reasons.append("1:3 Risk Reward")

    # =====================================
    # GRADE
    # =====================================

    if score >= 90:
        grade = "S"

    elif score >= 80:
        grade = "A"

    elif score >= 70:
        grade = "B"

    elif score >= 60:
        grade = "C"

    else:
        grade = "D"

    return {

        "score": score,

        "grade": grade,

        "reasons": reasons

    }