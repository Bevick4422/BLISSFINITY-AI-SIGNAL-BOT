
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Entry Selector v8
=====================================================

Purpose
-------
Select the highest probability entry setup.

Priority
--------
1. Left Shoulder
2. Break & Retest
3. Fresh H4 Level
4. Engulfing (Fallback)

=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict

from analysis.entry.left_shoulder import detect_left_shoulder
from analysis.entry.break_retest import detect_break_retest
# from analysis.entry.fresh_level import detect_fresh_level


# =====================================================
# DEFAULT FALLBACK ENTRY
# =====================================================

DEFAULT_CONFIDENCE = 70


def default_entry() -> Dict[str, Any]:
    """
    Default Engulfing entry when no premium setup exists.
    """

    return {

        "entry_type": "ENGULFING",

        "entry_price": None,

        "entry_data": {

            "valid": True,

            "confidence": DEFAULT_CONFIDENCE,

            "reason": "Default Engulfing Entry",

        }

    }


# =====================================================
# ENTRY SELECTOR
# =====================================================

def select_best_entry(
    df,
    level: float,
    direction: str,
) -> Dict[str, Any]:
    """
    Select the highest-quality entry.

    Priority

    1. Left Shoulder
    2. Break & Retest
    3. Fresh H4 Level
    4. Engulfing
    """

    try:

        # =================================================
        # 1. LEFT SHOULDER
        # =================================================

        left = detect_left_shoulder(
            df=df,
            level=level,
            direction=direction,
        )

        if left.get("valid", False):

            return {

                "entry_type": "LEFT_SHOULDER",

                "entry_price": left.get(
                    "left_shoulder",
                    level,
                ),

                "entry_data": left,

            }

        # =================================================
        # 2. BREAK & RETEST
        # =================================================

        break_retest = detect_break_retest(
            df=df,
            level=level,
            direction=direction,
        )

        if break_retest.get("valid", False):

            return {

                "entry_type": "BREAK_RETEST",

                "entry_price": break_retest.get(
                    "entry",
                    level,
                ),

                "entry_data": break_retest,

            }

        # =================================================
        # 3. FRESH H4 LEVEL
        # =================================================

        # fresh = detect_fresh_level(
        #     df=df,
        #     level=level,
        #     direction=direction,
        # )
        #
        # if fresh.get("valid", False):
        #
        #     return {
        #         "entry_type": "FRESH_LEVEL",
        #         "entry_price": fresh.get("entry", level),
        #         "entry_data": fresh,
        #     }

        # =================================================
        # 4. ENGULFING (Fallback)
        # =================================================

        return default_entry()

    except Exception as e:

        print("\n" + "=" * 60)
        print("ENTRY SELECTOR ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return {

            "entry_type": "NONE",

            "entry_price": None,

            "entry_data": {

                "valid": False,

                "confidence": 0,

                "reason": "Entry Selector Failure",

            },

        }