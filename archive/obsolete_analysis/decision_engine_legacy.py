
"""
BLISSFINITY AI SIGNAL BOT
RULE DECISION ENGINE

Purpose:
Validate institutional trading conditions.

This engine is RULE-BASED.
It does NOT calculate confidence or scores.
"""

def make_decision(
    weekly,
    daily_structure,
    daily_bos,
    h4_structure,
    h4_bos,
    liquidity,
    entry,
    risk,
):
    """
    Final rule validation.
    """

    approved = True
    reasons = []

    direction = weekly["bias"]

    # ======================================
    # WEEKLY BIAS
    # ======================================

    if weekly["bias"] == "NONE":
        approved = False
        reasons.append("No Weekly Bias")

    # ======================================
    # DAILY TREND
    # ======================================

    if daily_structure["trend"] == "RANGING":
        approved = False
        reasons.append("Daily Trend Not Clear")

    # ======================================
    # DAILY BOS
    # ======================================

    if not daily_bos["bos"]:
        approved = False
        reasons.append("Daily BOS Missing")

    # ======================================
    # H4 TREND
    # ======================================

    if h4_structure["trend"] == "RANGING":
        approved = False
        reasons.append("4H Trend Not Clear")

    # ======================================
    # H4 BOS
    # ======================================

    if not h4_bos["bos"]:
        approved = False
        reasons.append("4H BOS Missing")

    # ======================================
    # LIQUIDITY
    # ======================================

    if not liquidity["liquidity_grab"]:
        approved = False
        reasons.append("No Liquidity Sweep")

    # ======================================
    # ENTRY
    # ======================================

    if not entry["approved"]:
        approved = False
        reasons.append("No Entry Trigger")

    # ======================================
    # RISK
    # ======================================

    if risk["rr"] < 3:
        approved = False
        reasons.append("Risk Reward Below 1:3")

    # ======================================
    # DIRECTION ALIGNMENT
    # ======================================

    if approved:

        if daily_bos["direction"] != direction:
            approved = False
            reasons.append("Daily BOS Direction Mismatch")

        elif h4_bos["direction"] != direction:
            approved = False
            reasons.append("H4 BOS Direction Mismatch")

    # ======================================
    # FINAL RESULT
    # ======================================

    return {

        "approved": approved,

        "direction": direction if approved else None,

        "reasons": reasons

    }