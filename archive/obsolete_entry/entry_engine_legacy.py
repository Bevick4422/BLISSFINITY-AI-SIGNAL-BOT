"""
BLISSFINITY AI SIGNAL BOT
INSTITUTIONAL ENTRY ENGINE
"""


def detect_entry(
    fresh_levels,
    shoulder,
    inducement,
    supply_demand
):
    """
    Institutional Entry Logic

    Only ONE trigger is required.
    """

    reasons = []

    approved = False

    # ===================================
    # Fresh Institutional Level
    # ===================================

    if fresh_levels["has_fresh_level"]:

        approved = True

        reasons.append(
            "Fresh Institutional Level"
        )

    # ===================================
    # Left Shoulder
    # ===================================

    if shoulder["confirmed"]:

        approved = True

        reasons.append(
            shoulder["pattern"]
        )

    # ===================================
    # Inducement
    # ===================================

    if inducement["inducement"]:

        approved = True

        reasons.append(
            "Inducement"
        )

    # ===================================
    # Supply / Demand
    # ===================================

    if (

        supply_demand["in_supply"]

        or

        supply_demand["in_demand"]

    ):

        approved = True

        reasons.append(
            "Supply / Demand"
        )

    return {

        "approved": approved,

        "reasons": reasons

    }