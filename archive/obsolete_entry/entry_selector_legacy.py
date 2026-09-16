"""
=========================================================
BLISSFINITY SIGNAL
Entry Selector
=========================================================

Entry Rules

1. Bullish Engulfing
   - Uses confirmed Daily entry.
   - H4 BOS is not required.

2. Bearish Engulfing
   - Uses confirmed Daily entry.
   - H4 BOS is not required.

3. V Shape
   - Requires H4 BUY BOS.
   - Entry priority:
       LEFT_SHOULDER
       BREAK_RETEST
       FRESH_LEVEL
       POST_BOS_LEVEL

4. A Shape
   - Requires H4 SELL BOS.
   - Entry priority:
       LEFT_SHOULDER
       BREAK_RETEST
       FRESH_LEVEL
       POST_BOS_LEVEL

Important:
- The selector does not chase price.
- Maximum entry distance is 1%.
- Every rejection is printed for diagnostics.
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from analysis.entry.left_shoulder import detect_left_shoulder
from analysis.entry.break_retest import detect_break_retest
from analysis.entry.fresh_level import detect_fresh_level
from analysis.entry.post_bos_level import detect_post_bos_level


# =========================================================
# SETTINGS
# =========================================================

MAX_ENTRY_DISTANCE = 0.01


# =========================================================
# RESULT HELPERS
# =========================================================

def no_entry(reason: str) -> Dict[str, Any]:
    """
    Return a standard invalid-entry result.
    """

    return {
        "valid": False,
        "confidence": 0,
        "entry_price": None,
        "entry_type": None,
        "entry_data": {
            "valid": False,
            "confidence": 0,
            "reason": reason,
        },
    }


def valid_entry(
    entry_type: str,
    entry_price: float,
    entry_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return a standard valid-entry result.
    """

    data = entry_data if isinstance(entry_data, dict) else {}

    try:
        confidence = int(data.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0

    return {
        "valid": True,
        "confidence": confidence,
        "entry_price": float(entry_price),
        "entry_type": entry_type,
        "entry_data": data,
    }


# =========================================================
# CURRENT PRICE
# =========================================================

def get_current_price(df) -> Optional[float]:
    """
    Read the latest close from the supplied dataframe.
    """

    if df is None:
        return None

    try:
        if len(df) == 0:
            return None

        price = float(df.iloc[-1]["close"])

    except (
        AttributeError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
    ):
        return None

    if price <= 0:
        return None

    return price


# =========================================================
# ENTRY DISTANCE
# =========================================================

def calculate_entry_distance(
    entry_price: float,
    current_price: float,
) -> Optional[float]:
    """
    Calculate the percentage distance between entry and current price.
    """

    try:
        entry_price = float(entry_price)
        current_price = float(current_price)
    except (TypeError, ValueError):
        return None

    if entry_price <= 0 or current_price <= 0:
        return None

    return abs(current_price - entry_price) / current_price


def entry_is_close(
    entry_price: float,
    current_price: float,
) -> bool:
    """
    Confirm that the proposed entry is not more than 1% away.
    """

    distance = calculate_entry_distance(
        entry_price,
        current_price,
    )

    if distance is None:
        return False

    return distance <= MAX_ENTRY_DISTANCE


# =========================================================
# SETUP NORMALIZATION
# =========================================================

def normalize_setup(setup: Any) -> str:
    """
    Normalize setup names for reliable comparisons.
    """

    if setup is None:
        return ""

    return (
        str(setup)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


# =========================================================
# RESULT DISPLAY
# =========================================================

def print_result(
    name: str,
    result: Optional[Dict[str, Any]],
) -> None:
    """
    Print a consistent diagnostic result.
    """

    if not isinstance(result, dict):
        print(f"{name} | Rejected: No result returned")
        return

    print(f"    Valid      : {result.get('valid')}")
    print(f"    Entry      : {result.get('entry')}")
    print(f"    Confidence : {result.get('confidence')}")
    print(f"    Reason     : {result.get('reason')}")

    if "break_index" in result:
        print(f"    Break Idx  : {result.get('break_index')}")

    if "retest_index" in result:
        print(f"    Retest Idx : {result.get('retest_index')}")

    if "level_index" in result:
        print(f"    Level Idx  : {result.get('level_index')}")

    if "mitigated_index" in result:
        print(f"    Mitigated  : {result.get('mitigated_index')}")


# =========================================================
# ENTRY VALIDATION
# =========================================================

def validate_candidate(
    name: str,
    result: Optional[Dict[str, Any]],
    current_price: float,
) -> Optional[Dict[str, Any]]:
    """
    Validate a candidate entry and reject stale entries.
    """

    if not isinstance(result, dict):
        print(f"{name} | Rejected: No result returned")
        return None

    if not result.get("valid"):
        print(f"{name} | Rejected")
        print(f"    Reason     : {result.get('reason')}")
        print(f"    Confidence : {result.get('confidence', 0)}")
        return None

    entry = result.get("entry")

    if entry is None:
        print(f"{name} | Rejected: Entry unavailable")
        return None

    try:
        entry = float(entry)
    except (TypeError, ValueError):
        print(f"{name} | Rejected: Invalid entry")
        return None

    distance = calculate_entry_distance(
        entry,
        current_price,
    )

    if distance is None:
        print(f"{name} | Rejected: Invalid distance")
        return None

    print(f"    Distance   : {distance:.2%}")
    print(f"    Maximum    : {MAX_ENTRY_DISTANCE:.2%}")

    if not entry_is_close(entry, current_price):
        print(f"{name} | Rejected: Entry stale")
        return None

    print(f"{name} | VALID")

    return valid_entry(
        name,
        entry,
        result,
    )


# =========================================================
# DAILY ENGULFING ENTRY
# =========================================================

def select_engulfing_entry(
    df,
    direction: str,
    daily_entry: Optional[float],
) -> Dict[str, Any]:
    """
    Select an entry for Daily bullish or bearish engulfing.
    """

    current_price = get_current_price(df)

    print()
    print("DAILY ENGULFING ENTRY")
    print("-" * 60)
    print(f"Direction   : {direction}")
    print(f"Daily Entry : {daily_entry}")
    print(f"Current     : {current_price}")

    if daily_entry is None:
        print("RESULT: Daily entry unavailable")
        return no_entry("Engulfing entry price unavailable")

    try:
        daily_entry = float(daily_entry)
    except (TypeError, ValueError):
        return no_entry("Invalid engulfing entry price")

    if daily_entry <= 0:
        return no_entry("Invalid engulfing entry price")

    if current_price is None:
        return no_entry("Current price unavailable")

    distance = calculate_entry_distance(
        daily_entry,
        current_price,
    )

    print(f"Distance    : {distance:.2%}")
    print(f"Maximum     : {MAX_ENTRY_DISTANCE:.2%}")

    if not entry_is_close(daily_entry, current_price):
        print("RESULT: DAILY ENTRY STALE")
        return no_entry("Engulfing entry is stale")

    print("RESULT: VALID DAILY ENTRY")

    return valid_entry(
        "ENGULFING",
        daily_entry,
        {
            "valid": True,
            "confidence": 90,
            "entry": daily_entry,
            "current_price": current_price,
            "distance": distance,
            "reason": "Confirmed Daily Engulfing Entry",
        },
    )


# =========================================================
# STRUCTURAL ENTRY
# =========================================================

def select_structural_entry(
    df,
    direction: str,
    level: Optional[float],
    level_index: Optional[int],
    bos_level: Optional[float],
    bos_index: Any = None,
) -> Dict[str, Any]:
    """
    Select a structural entry using the defined priority.
    """

    current_price = get_current_price(df)

    if current_price is None:
        return no_entry("Current price unavailable")

    if level is None:
        return no_entry("Daily V/A level unavailable")

    try:
        level = float(level)
    except (TypeError, ValueError):
        return no_entry("Invalid Daily V/A level")

    if level <= 0:
        return no_entry("Invalid Daily V/A level")

    print()
    print("STRUCTURAL ENTRY SELECTOR")
    print("-" * 60)
    print(f"Direction       : {direction}")
    print(f"Daily V/A Level : {level}")
    print(f"H4 BOS Level    : {bos_level}")
    print(f"H4 BOS Index    : {bos_index}")
    print(f"Current Price   : {current_price}")
    print(f"Max Entry Dist. : {MAX_ENTRY_DISTANCE:.2%}")

    # =====================================================
    # 1. LEFT SHOULDER
    # =====================================================

    print()
    print("[1] LEFT SHOULDER")

    try:
        result = detect_left_shoulder(
            df=df,
            level=level,
            direction=direction,
        )
    except Exception as exc:
        print(f"LEFT SHOULDER | ERROR: {type(exc).__name__}: {exc}")
        result = None

    print_result("LEFT SHOULDER", result)

    valid = validate_candidate(
        "LEFT_SHOULDER",
        result,
        current_price,
    )

    if valid is not None:
        return valid

    # =====================================================
    # 2. BREAK AND RETEST
    # =====================================================

    print()
    print("[2] BREAK & RETEST")

    if bos_level is None:
        print("BREAK & RETEST | Skipped: No H4 BOS level")
    else:
        try:
            bos_level = float(bos_level)
        except (TypeError, ValueError):
            bos_level = None

        if bos_level is None:
            print("BREAK & RETEST | Skipped: Invalid BOS level")
        else:
            try:
                result = detect_break_retest(
                    df=df,
                    level=bos_level,
                    direction=direction,
                )
            except Exception as exc:
                print(
                    "BREAK & RETEST | ERROR: "
                    f"{type(exc).__name__}: {exc}"
                )
                result = None

            print_result("BREAK & RETEST", result)

            valid = validate_candidate(
                "BREAK_RETEST",
                result,
                current_price,
            )

            if valid is not None:
                return valid

    # =====================================================
    # 3. FRESH DAILY LEVEL
    # =====================================================

    print()
    print("[3] FRESH LEVEL")

    if level_index is None:
        print("FRESH LEVEL | Skipped: No level index")
    else:
        try:
            level_index = int(level_index)
        except (TypeError, ValueError):
            level_index = None

        if level_index is None:
            print("FRESH LEVEL | Skipped: Invalid level index")
        else:
            try:
                result = detect_fresh_level(
                    df=df,
                    level=level,
                    direction=direction,
                    level_index=level_index,
                )
            except Exception as exc:
                print(
                    "FRESH LEVEL | ERROR: "
                    f"{type(exc).__name__}: {exc}"
                )
                result = None

            print_result("FRESH LEVEL", result)

            valid = validate_candidate(
                "FRESH_LEVEL",
                result,
                current_price,
            )

            if valid is not None:
                return valid

    # =====================================================
    # 4. POST-BOS FRESH LEVEL
    # =====================================================

    print()
    print("[4] POST-BOS FRESH LEVEL")

    if bos_index is None:
        print(
            "POST-BOS LEVEL | "
            "Skipped: No H4 BOS index"
        )
    else:
        try:
            result = detect_post_bos_level(
                df=df,
                bos_index=bos_index,
                direction=direction,
            )
        except Exception as exc:
            print(
                "POST-BOS LEVEL | ERROR: "
                f"{type(exc).__name__}: {exc}"
            )
            result = None

        print_result("POST-BOS LEVEL", result)

        valid = validate_candidate(
            "POST_BOS_LEVEL",
            result,
            current_price,
        )

        if valid is not None:
            return valid

    # =====================================================
    # NO VALID STRUCTURAL ENTRY
    # =====================================================

    print()
    print("STRUCTURAL ENTRY SELECTOR | NO VALID ENTRY")

    return no_entry(
        "No valid structural entry method"
    )


# =========================================================
# MAIN SELECTOR
# =========================================================

def select_best_entry(
    df,
    level: Optional[float],
    direction: str,
    level_index: Optional[int] = None,
    bos_level: Optional[float] = None,
    setup: Optional[str] = None,
    daily_entry: Optional[float] = None,
    bos_index: Any = None,
) -> Dict[str, Any]:
    """
    Main entry-selection router.
    """

    if df is None:
        return no_entry("No H4 market data")

    try:
        if len(df) == 0:
            return no_entry("No H4 market data")
    except TypeError:
        return no_entry("Invalid H4 market data")

    if direction not in ("BUY", "SELL"):
        return no_entry("Invalid direction")

    normalized_setup = normalize_setup(setup)

    print()
    print("ENTRY SELECTOR")
    print("-" * 60)
    print(f"Setup     : {setup}")
    print(f"Direction : {direction}")

    # =====================================================
    # DAILY ENGULFING
    # =====================================================

    if normalized_setup in (
        "bullish engulfing",
        "bearish engulfing",
    ):
        print("Path      : DAILY ENGULFING")

        return select_engulfing_entry(
            df=df,
            direction=direction,
            daily_entry=daily_entry,
        )

    # =====================================================
    # STRUCTURAL SETUPS
    # =====================================================

    if normalized_setup in (
        "v shape",
        "a shape",
    ):
        print("Path      : STRUCTURAL")

        if normalized_setup == "v shape":
            if direction != "BUY":
                return no_entry(
                    "V Shape requires BUY direction"
                )

        if normalized_setup == "a shape":
            if direction != "SELL":
                return no_entry(
                    "A Shape requires SELL direction"
                )

        if bos_level is None:
            print("RESULT: WAITING FOR H4 BOS")

            return no_entry(
                "H4 BOS required"
            )

        return select_structural_entry(
            df=df,
            direction=direction,
            level=level,
            level_index=level_index,
            bos_level=bos_level,
            bos_index=bos_index,
        )

    # =====================================================
    # UNKNOWN SETUP
    # =====================================================

    print(
        f"RESULT: Unsupported setup '{setup}'"
    )

    return no_entry(
        "Unsupported Daily setup"
    )


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "select_best_entry",
    "select_engulfing_entry",
    "select_structural_entry",
    "get_current_price",
    "entry_is_close",
    "calculate_entry_distance",
]