"""
============================================================
BLISSFINITY SIGNAL
Daily Structure Engine
============================================================

SOURCE OF TRUTH
----------------
Daily is always analyzed first.

Rules:
1. Only completed Daily candles may be used.
2. Trend is determined from price structure.
3. Bullish trend = HH -> HL -> HH -> HL.
4. Bearish trend = LL -> LH -> LL -> LH.
5. V Shape = RED body -> GREEN body.
6. A Shape = GREEN body -> RED body.
7. Daily Engulfing is BODY ONLY.
8. A clean Daily Engulfing at the relevant A/V level is a
   continuation setup and does NOT require H4 BOS.
9. If the same Daily candle is both an engulfing and a
   rejection of the relevant A/V level, the result is NO SIGNAL.
10. A Daily rejection without engulfing follows the structural
    pathway and requires H4 BOS + Break/Retest.
============================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


MIN_CANDLES = 8


# ============================================================
# RESULT HELPERS
# ============================================================

def _empty(reason: str) -> Dict[str, Any]:
    return {
        "valid": False,
        "trend": "RANGE",
        "structure": [],
        "swings": [],
        "setup": None,
        "direction": None,
        "level": None,
        "level_index": None,
        "setup_candle_index": None,
        "setup_candle_timestamp": None,
        "entry": None,
        "retest_required": False,
        "entry_mode": None,
        "reason": reason,
    }


# ============================================================
# CANDLE HELPERS
# ============================================================

def _candle_body_color(
    candle: pd.Series,
) -> Optional[str]:
    """Return GREEN, RED, or None for a doji."""

    try:
        open_price = float(candle["open"])
        close_price = float(candle["close"])
    except (KeyError, TypeError, ValueError):
        return None

    if close_price > open_price:
        return "GREEN"

    if close_price < open_price:
        return "RED"

    return None


def _body_engulfs(
    previous: pd.Series,
    current: pd.Series,
) -> bool:
    """
    Body-only engulfing.

    Bullish:
        previous RED
        current GREEN
        current body covers previous body

    Bearish:
        previous GREEN
        current RED
        current body covers previous body
    """

    previous_color = _candle_body_color(previous)
    current_color = _candle_body_color(current)

    if (
        previous_color == "RED"
        and current_color == "GREEN"
    ):
        return (
            float(current["open"])
            <= float(previous["close"])
            and float(current["close"])
            >= float(previous["open"])
        )

    if (
        previous_color == "GREEN"
        and current_color == "RED"
    ):
        return (
            float(current["open"])
            >= float(previous["close"])
            and float(current["close"])
            <= float(previous["open"])
        )

    return False


# ============================================================
# SWING STRUCTURE
# ============================================================

def _classify_swings(
    df: pd.DataFrame,
) -> list[Dict[str, Any]]:
    """
    Identify confirmed local structural highs and lows.

    Only completed candles are supplied by the caller.
    """

    if len(df) < 3:
        return []

    records: list[Dict[str, Any]] = []

    for i in range(1, len(df) - 1):

        previous = df.iloc[i - 1]
        current = df.iloc[i]
        following = df.iloc[i + 1]

        try:
            high = float(current["high"])
            low = float(current["low"])

            previous_high = float(previous["high"])
            previous_low = float(previous["low"])

            following_high = float(following["high"])
            following_low = float(following["low"])

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

        if (
            high > previous_high
            and high >= following_high
        ):
            records.append(
                {
                    "kind": "HIGH",
                    "index": i,
                    "price": high,
                    "timestamp": df.index[i],
                }
            )

        if (
            low < previous_low
            and low <= following_low
        ):
            records.append(
                {
                    "kind": "LOW",
                    "index": i,
                    "price": low,
                    "timestamp": df.index[i],
                }
            )

    return records


def _trend_from_structure(
    swings: list[Dict[str, Any]],
) -> tuple[str, list[str]]:
    """
    Determine Daily trend from structural extremes.

    Bullish:
        last 3 highs rising
        last 3 lows rising

    Bearish:
        last 3 highs falling
        last 3 lows falling
    """

    highs = [
        swing
        for swing in swings
        if swing["kind"] == "HIGH"
    ]

    lows = [
        swing
        for swing in swings
        if swing["kind"] == "LOW"
    ]

    if len(highs) < 3 or len(lows) < 3:
        return "RANGE", []

    recent_highs = highs[-3:]
    recent_lows = lows[-3:]

    bullish = (
        recent_highs[-1]["price"]
        > recent_highs[-2]["price"]
        > recent_highs[-3]["price"]
        and
        recent_lows[-1]["price"]
        > recent_lows[-2]["price"]
        > recent_lows[-3]["price"]
    )

    bearish = (
        recent_highs[-1]["price"]
        < recent_highs[-2]["price"]
        < recent_highs[-3]["price"]
        and
        recent_lows[-1]["price"]
        < recent_lows[-2]["price"]
        < recent_lows[-3]["price"]
    )

    if bullish:
        return "BULLISH", [
            "HH",
            "HL",
            "HH",
            "HL",
        ]

    if bearish:
        return "BEARISH", [
            "LL",
            "LH",
            "LL",
            "LH",
        ]

    labels: list[str] = []

    for previous, current in zip(
        highs[-4:-1],
        highs[-3:],
    ):
        labels.append(
            "HH"
            if current["price"] > previous["price"]
            else "LH"
        )

    for previous, current in zip(
        lows[-4:-1],
        lows[-3:],
    ):
        labels.append(
            "HL"
            if current["price"] > previous["price"]
            else "LL"
        )

    return "RANGE", labels


# ============================================================
# A / V FORMATIONS
# ============================================================

def _find_va(
    df: pd.DataFrame,
    trend: str,
) -> Optional[Dict[str, Any]]:
    """
    Find the latest trend-compatible V/A formation.

    V:
        RED -> GREEN
        valid in bullish trend

    A:
        GREEN -> RED
        valid in bearish trend

    Level:
        open of the second candle.
    """

    if len(df) < 2:
        return None

    for i in range(
        len(df) - 1,
        0,
        -1,
    ):

        first = df.iloc[i - 1]
        second = df.iloc[i]

        first_color = _candle_body_color(first)
        second_color = _candle_body_color(second)

        # -----------------------------
        # V SHAPE
        # -----------------------------

        if (
            first_color == "RED"
            and second_color == "GREEN"
        ):
            if trend != "BULLISH":
                continue

            return {
                "formation_type": "V_SHAPE",
                "direction": "BUY",
                "first_candle_index": i - 1,
                "second_candle_index": i,
                "level": float(second["open"]),
                "level_index": i,
            }

        # -----------------------------
        # A SHAPE
        # -----------------------------

        if (
            first_color == "GREEN"
            and second_color == "RED"
        ):
            if trend != "BEARISH":
                continue

            return {
                "formation_type": "A_SHAPE",
                "direction": "SELL",
                "first_candle_index": i - 1,
                "second_candle_index": i,
                "level": float(second["open"]),
                "level_index": i,
            }

    return None


def _find_latest_va_levels(
    df: pd.DataFrame,
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Find the latest A and V formations independently.

    Used specifically for Daily Engulfing A/V-level
    interaction and conflict detection.

    No trend restriction is applied here.
    """

    result: Dict[str, Optional[Dict[str, Any]]] = {
        "A_SHAPE": None,
        "V_SHAPE": None,
    }

    if len(df) < 2:
        return result

    for i in range(
        len(df) - 1,
        0,
        -1,
    ):

        first = df.iloc[i - 1]
        second = df.iloc[i]

        first_color = _candle_body_color(first)
        second_color = _candle_body_color(second)

        if (
            result["V_SHAPE"] is None
            and first_color == "RED"
            and second_color == "GREEN"
        ):
            result["V_SHAPE"] = {
                "formation_type": "V_SHAPE",
                "first_candle_index": i - 1,
                "second_candle_index": i,
                "level": float(second["open"]),
                "level_index": i,
            }

        if (
            result["A_SHAPE"] is None
            and first_color == "GREEN"
            and second_color == "RED"
        ):
            result["A_SHAPE"] = {
                "formation_type": "A_SHAPE",
                "first_candle_index": i - 1,
                "second_candle_index": i,
                "level": float(second["open"]),
                "level_index": i,
            }

        if (
            result["A_SHAPE"] is not None
            and result["V_SHAPE"] is not None
        ):
            break

    return result


# ============================================================
# DAILY ENGULFING
# ============================================================

def _find_daily_engulfing(
    df: pd.DataFrame,
) -> Optional[Dict[str, Any]]:
    """
    Detect the latest completed Daily body engulfing.
    """

    if len(df) < 2:
        return None

    previous = df.iloc[-2]
    current = df.iloc[-1]

    previous_color = _candle_body_color(previous)
    current_color = _candle_body_color(current)

    # -----------------------------
    # BULLISH
    # -----------------------------

    if (
        previous_color == "RED"
        and current_color == "GREEN"
        and _body_engulfs(
            previous,
            current,
        )
    ):
        return {
            "setup": "Bullish Engulfing",
            "direction": "BUY",
            "entry": float(current["close"]),
            "setup_candle_index": len(df) - 1,
            "setup_candle_timestamp": df.index[-1],
        }

    # -----------------------------
    # BEARISH
    # -----------------------------

    if (
        previous_color == "GREEN"
        and current_color == "RED"
        and _body_engulfs(
            previous,
            current,
        )
    ):
        return {
            "setup": "Bearish Engulfing",
            "direction": "SELL",
            "entry": float(current["close"]),
            "setup_candle_index": len(df) - 1,
            "setup_candle_timestamp": df.index[-1],
        }

    return None


# ============================================================
# LEVEL INTERACTION
# ============================================================

def _candle_interacts_with_level(
    candle: pd.Series,
    level: float,
) -> bool:
    """
    A candle interacts with a structural level when
    the level lies within its full high/low range.
    """

    try:
        high = float(candle["high"])
        low = float(candle["low"])
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return False

    return low <= level <= high


# ============================================================
# SAME-CANDLE REJECTION
# ============================================================

def _is_bullish_rejection(
    candle: pd.Series,
    level: float,
) -> bool:
    """
    Bullish-direction rejection of resistance.

    Price reaches the level but the completed candle
    closes back below it.
    """

    try:
        high = float(candle["high"])
        close = float(candle["close"])
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return False

    return (
        high >= level
        and close < level
    )


def _is_bearish_rejection(
    candle: pd.Series,
    level: float,
) -> bool:
    """
    Bearish-direction rejection of demand.

    Price reaches the level but the completed candle
    closes back above it.
    """

    try:
        low = float(candle["low"])
        close = float(candle["close"])
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return False

    return (
        low <= level
        and close > level
    )


# ============================================================
# ENGULFING LEVEL VALIDATION
# ============================================================

def _check_engulfing_level_conflict(
    df: pd.DataFrame,
    engulfing: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Determine whether the completed Daily engulfing is:

        1. clean continuation at the relevant A/V level
        2. same-candle rejection conflict
        3. not interacting with a relevant A/V level

    Locked relationships:

        Bullish engulfing
            -> relevant A Shape / resistance

        Bearish engulfing
            -> relevant V Shape / demand
    """

    current = df.iloc[-1]

    direction = engulfing["direction"]

    levels = _find_latest_va_levels(df)

    # --------------------------------------------------------
    # BULLISH ENGULFING -> A SHAPE / RESISTANCE
    # --------------------------------------------------------

    if direction == "BUY":

        a_info = levels.get("A_SHAPE")

        if a_info is None:
            return {
                "interacts": False,
                "conflict": False,
                "level": None,
                "level_index": None,
                "reason": "No relevant A Shape level",
            }

        level = float(a_info["level"])

        interacts = _candle_interacts_with_level(
            current,
            level,
        )

        if not interacts:
            return {
                "interacts": False,
                "conflict": False,
                "level": level,
                "level_index": a_info["level_index"],
                "reason": (
                    "Bullish engulfing does not interact "
                    "with A Shape"
                ),
            }

        rejection = _is_bullish_rejection(
            current,
            level,
        )

        return {
            "interacts": True,
            "conflict": rejection,
            "level": level,
            "level_index": a_info["level_index"],
            "reason": (
                "Bullish engulfing + same-candle "
                "resistance rejection"
                if rejection
                else "Clean bullish engulfing at A Shape"
            ),
        }

    # --------------------------------------------------------
    # BEARISH ENGULFING -> V SHAPE / DEMAND
    # --------------------------------------------------------

    if direction == "SELL":

        v_info = levels.get("V_SHAPE")

        if v_info is None:
            return {
                "interacts": False,
                "conflict": False,
                "level": None,
                "level_index": None,
                "reason": "No relevant V Shape level",
            }

        level = float(v_info["level"])

        interacts = _candle_interacts_with_level(
            current,
            level,
        )

        if not interacts:
            return {
                "interacts": False,
                "conflict": False,
                "level": level,
                "level_index": v_info["level_index"],
                "reason": (
                    "Bearish engulfing does not interact "
                    "with V Shape"
                ),
            }

        rejection = _is_bearish_rejection(
            current,
            level,
        )

        return {
            "interacts": True,
            "conflict": rejection,
            "level": level,
            "level_index": v_info["level_index"],
            "reason": (
                "Bearish engulfing + same-candle "
                "demand rejection"
                if rejection
                else "Clean bearish engulfing at V Shape"
            ),
        }

    return {
        "interacts": False,
        "conflict": False,
        "level": None,
        "level_index": None,
        "reason": "Unknown engulfing direction",
    }


# ============================================================
# DAILY STRUCTURE
# ============================================================

def detect_daily_structure(
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Return the completed Daily structural state.

    The dataframe must already have passed the
    canonical completed-candle gate.
    """

    if df is None or len(df) < MIN_CANDLES:
        return _empty(
            "Insufficient completed Daily candles"
        )

    required = {
        "open",
        "high",
        "low",
        "close",
        "volume",
    }

    missing = required.difference(df.columns)

    if missing:
        return _empty(
            f"Missing Daily columns: {sorted(missing)}"
        )

    swings = _classify_swings(df)

    trend, structure = _trend_from_structure(
        swings
    )

    return {
        "valid": True,
        "trend": trend,
        "structure": structure,
        "swings": swings,
        "setup": None,
        "direction": None,
        "level": None,
        "level_index": None,
        "setup_candle_index": None,
        "setup_candle_timestamp": None,
        "entry": None,
        "retest_required": False,
        "entry_mode": None,
        "reason": (
            "RANGE"
            if trend == "RANGE"
            else "Structure detected"
        ),
    }




def _find_daily_rejection(
    df: pd.DataFrame,
) -> Optional[Dict[str, Any]]:
    """Detect Daily rejection at confirmed Daily structural swing levels.

    SELL: latest candle reaches a prior confirmed swing high and closes below.
    BUY: latest candle reaches a prior confirmed swing low and closes above.

    Multiple distinct qualifying levels or mixed directions are ambiguous.
    """
    if df is None or len(df) < 3:
        return None

    swings = _classify_swings(df)
    candle = df.iloc[-1]

    high = float(candle["high"])
    low = float(candle["low"])
    close = float(candle["close"])

    candidates = []

    for swing in swings:
        kind = swing.get("kind")
        level = float(swing["price"])
        level_index = int(swing["index"])

        # A rejection level must be confirmed before the latest candle.
        if level_index >= len(df) - 1:
            continue

        if kind == "HIGH" and high >= level and close < level:
            candidates.append({
                "formation_type": "A_SHAPE",
                "direction": "SELL",
                "level": level,
                "level_index": level_index,
            })

        elif kind == "LOW" and low <= level and close > level:
            candidates.append({
                "formation_type": "V_SHAPE",
                "direction": "BUY",
                "level": level,
                "level_index": level_index,
            })

    if not candidates:
        return None

    directions = {item["direction"] for item in candidates}
    levels = {item["level"] for item in candidates}

    if len(directions) > 1 or len(levels) > 1:
        return {
            "ambiguous": True,
            "formation_type": "DAILY_REJECTION_AMBIGUOUS",
            "direction": None,
            "level": None,
            "level_index": None,
            "rejected_levels": candidates,
        }

    chosen = max(candidates, key=lambda item: item["level_index"])
    chosen["ambiguous"] = False
    chosen["rejected_levels"] = candidates

    return chosen

# DAILY SETUP
# ============================================================

def detect_daily_setup(
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Build the final Daily setup.

    Priority:

        1. Daily Engulfing
        2. Engulfing must interact with relevant A/V level
        3. Engulfing conflict -> NO SIGNAL
        4. Range gate
        5. V/A structural setup
    """

    structure = detect_daily_structure(df)

    if not structure["valid"]:
        return structure

    # ========================================================
    # 1. DAILY ENGULFING
    # ========================================================

    engulfing = _find_daily_engulfing(df)

    if engulfing is not None:

        conflict = _check_engulfing_level_conflict(
            df,
            engulfing,
        )

        # ----------------------------------------------------
        # NO RELEVANT A/V LEVEL OR NO INTERACTION
        # ----------------------------------------------------

        if not conflict["interacts"]:

            structure.update(
                {
                    "setup": None,
                    "direction": None,
                    "level": conflict["level"],
                    "level_index": conflict["level_index"],
                    "setup_candle_index": engulfing[
                        "setup_candle_index"
                    ],
                    "setup_candle_timestamp": engulfing[
                        "setup_candle_timestamp"
                    ],
                    "entry": None,
                    "retest_required": False,
                    "entry_mode": None,
                    "reason": (
                        "ENGULFING_NO_RELEVANT_AV_INTERACTION"
                    ),
                }
            )

            return structure

        # ----------------------------------------------------
        # SAME-CANDLE CONFLICT
        # ----------------------------------------------------

        if conflict["conflict"]:

            structure.update(
                {
                    "setup": None,
                    "direction": None,
                    "level": conflict["level"],
                    "level_index": conflict["level_index"],
                    "setup_candle_index": engulfing[
                        "setup_candle_index"
                    ],
                    "setup_candle_timestamp": engulfing[
                        "setup_candle_timestamp"
                    ],
                    "entry": None,
                    "retest_required": False,
                    "entry_mode": None,
                    "reason": (
                        "ENGULFING_REJECTION_CONFLICT"
                    ),
                }
            )

            return structure

        # ----------------------------------------------------
        # CLEAN ENGULFING
        #
        # Relevant A/V interaction confirmed.
        # H4 BOS is NOT required.
        # ----------------------------------------------------

        structure.update(
            {
                "setup": engulfing["setup"],
                "direction": engulfing["direction"],
                "level": conflict["level"],
                "level_index": conflict["level_index"],
                "setup_candle_index": engulfing[
                    "setup_candle_index"
                ],
                "setup_candle_timestamp": engulfing[
                    "setup_candle_timestamp"
                ],
                "entry": engulfing["entry"],
                "retest_required": False,
                "entry_mode": "DAILY_CLOSE",
                "reason": (
                    "Clean Daily engulfing continuation"
                ),
            }
        )

        return structure

    # ========================================================
    # 2. DAILY REJECTION (after engulfing priority, before range gate)
    rejection = _find_daily_rejection(df)
    if rejection is not None:
        if rejection.get("ambiguous"):
            structure.update({
                "setup": None,
                "direction": None,
                "level": None,
                "level_index": None,
                "setup_candle_index": len(df) - 1,
                "setup_candle_timestamp": df.index[-1],
                "entry": None,
                "retest_required": True,
                "entry_mode": "H4_PATHWAY",
                "reason": "DAILY_REJECTION_AMBIGUOUS_LEVELS_NO_SIGNAL",
            })
            return structure

        structure.update({
            "setup": rejection["formation_type"],
            "direction": rejection["direction"],
            "level": rejection["level"],
            "level_index": rejection["level_index"],
            "setup_candle_index": len(df) - 1,
            "setup_candle_timestamp": df.index[-1],
            "entry": None,
            "retest_required": True,
            "entry_mode": "H4_PATHWAY",
            "reason": "DAILY_REJECTION_REQUIRES_MATCHING_H4_BOS_AND_RETEST",
            "rejected_levels": rejection["rejected_levels"],
        })
        return structure

    # 2. RANGE GATE
    #
    # No engulfing.
    # Therefore structural V/A setups only.
    # ========================================================

    if structure["trend"] == "RANGE":

        structure["reason"] = (
            "RANGING_MARKET_NO_SIGNAL"
        )

        return structure

    # ========================================================
    # 3. V/A STRUCTURAL PATHWAY
    # ========================================================

    va = _find_va(
        df,
        structure["trend"],
    )

    if va is not None:

        structure.update(
            {
                "setup": va["formation_type"],
                "direction": va["direction"],
                "level": va["level"],
                "level_index": va["level_index"],
                "setup_candle_index": va[
                    "second_candle_index"
                ],
                "setup_candle_timestamp": df.index[
                    va["second_candle_index"]
                ],
                "entry": None,
                "retest_required": True,
                "entry_mode": "H4_PATHWAY",
                "reason": (
                    "Body-only V/A structural setup"
                ),
            }
        )

        return structure

    # ========================================================
    # 4. NO VALID DAILY SETUP
    # ========================================================

    structure["reason"] = (
        "No valid Daily setup"
    )

    return structure


__all__ = [
    "detect_daily_structure",
    "detect_daily_setup",
]


