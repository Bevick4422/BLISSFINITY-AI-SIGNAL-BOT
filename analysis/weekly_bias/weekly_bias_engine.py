
"""
BLISSFINITY AI SIGNAL BOT
INSTITUTIONAL WEEKLY BIAS ENGINE
"""

from analysis.weekly_key_levels.weekly_key_level_engine import (
    detect_weekly_key_levels,
)

from analysis.weekly_fresh_levels.weekly_fresh_level_engine import (
    detect_fresh_weekly_levels,
)

from analysis.weekly_rejection.weekly_rejection_engine import (
    detect_weekly_rejection,
)


def detect_weekly_bias(df):
    """
    Institutional Weekly Bias

    Workflow

    Weekly OHLC
        ↓
    Detect A/V Levels
        ↓
    Remove Mitigated Levels
        ↓
    Detect Weekly Rejection
        ↓
    Return BUY / SELL Bias
    """

    # ==========================================
    # STEP 1
    # Weekly Institutional Levels
    # ==========================================

    weekly_levels = detect_weekly_key_levels(df)

    # ==========================================
    # STEP 2
    # Fresh Levels
    # ==========================================

    fresh_levels = detect_fresh_weekly_levels(
        df,
        weekly_levels
    )

    # ==========================================
    # STEP 3
    # Weekly Rejection
    # ==========================================

    rejection = detect_weekly_rejection(
        df,
        fresh_levels
    )

    # ==========================================
    # STEP 4
    # No Bias
    # ==========================================

    if not rejection["rejected"]:

        return {

            "bias": "NONE",

            "confirmed": False,

            "pattern": None,

            "weekly_level": None,

            "reason": "No Weekly Rejection"

        }

    # ==========================================
    # BUY
    # ==========================================

    if rejection["direction"] == "BUY":

        return {

            "bias": "BUY",

            "confirmed": True,

            "pattern": rejection["pattern"],

            "weekly_level": rejection["level"],

            "reason": rejection["reason"]

        }

    # ==========================================
    # SELL
    # ==========================================

    return {

        "bias": "SELL",

        "confirmed": True,

        "pattern": rejection["pattern"],

        "weekly_level": rejection["level"],

        "reason": rejection["reason"]

    }