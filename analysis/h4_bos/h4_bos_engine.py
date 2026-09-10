"""
BLISSFINITY SIGNAL
4H Break of Structure Engine

Rules:
    1. Swing highs/lows must be confirmed.
    2. Bullish BOS requires a CLOSED candle body close
       above the latest confirmed swing high.
    3. Bearish BOS requires a CLOSED candle body close
       below the latest confirmed swing low.
    4. Wick-only breaks do not count.
    5. The currently forming candle is excluded.
    6. Only a break confirmed by the latest closed candle
       is considered a CURRENT BOS.
    7. If no current BOS exists, all BOS fields are cleared.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


# ==========================================================
# SETTINGS
# ==========================================================

SWING_LOOKBACK = 5


# ==========================================================
# RESULT HELPERS
# ==========================================================

def no_bos() -> Dict[str, Any]:
    """
    Clean result when there is no current confirmed BOS.
    """

    return {
        "bos": False,
        "direction": None,
        "broken_level": None,
        "swing_high": None,
        "swing_low": None,
        "break_index": None,
        "swing_high_index": None,
        "swing_low_index": None,
    }


# ==========================================================
# DATA VALIDATION
# ==========================================================

def _validate_dataframe(df: pd.DataFrame) -> bool:

    if df is None:
        return False

    if not isinstance(df, pd.DataFrame):
        return False

    if df.empty:
        return False

    required = {
        "open",
        "high",
        "low",
        "close",
    }

    if not required.issubset(df.columns):
        return False

    minimum = (SWING_LOOKBACK * 2) + 5

    if len(df) < minimum:
        return False

    return True


# ==========================================================
# SWING HIGH
# ==========================================================

def _find_latest_swing_high(
    df: pd.DataFrame,
) -> Optional[Dict[str, Any]]:

    n = len(df)

    start = SWING_LOOKBACK
    end = n - SWING_LOOKBACK

    for i in range(
        end - 1,
        start - 1,
        -1,
    ):

        center = float(
            df["high"].iloc[i]
        )

        left = df["high"].iloc[
            i - SWING_LOOKBACK:i
        ]

        right = df["high"].iloc[
            i + 1:i + SWING_LOOKBACK + 1
        ]

        if (
            center > float(left.max())
            and
            center > float(right.max())
        ):

            return {
                "price": center,
                "index": df.index[i],
                "position": i,
            }

    return None


# ==========================================================
# SWING LOW
# ==========================================================

def _find_latest_swing_low(
    df: pd.DataFrame,
) -> Optional[Dict[str, Any]]:

    n = len(df)

    start = SWING_LOOKBACK
    end = n - SWING_LOOKBACK

    for i in range(
        end - 1,
        start - 1,
        -1,
    ):

        center = float(
            df["low"].iloc[i]
        )

        left = df["low"].iloc[
            i - SWING_LOOKBACK:i
        ]

        right = df["low"].iloc[
            i + 1:i + SWING_LOOKBACK + 1
        ]

        if (
            center < float(left.min())
            and
            center < float(right.min())
        ):

            return {
                "price": center,
                "index": df.index[i],
                "position": i,
            }

    return None


# ==========================================================
# CURRENT BULLISH BOS
# ==========================================================

def _find_current_bullish_bos(
    df: pd.DataFrame,
    swing_high: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    A bullish BOS is valid only when the LATEST CLOSED
    candle closes above the confirmed swing high.
    """

    level = float(
        swing_high["price"]
    )

    latest_position = len(df) - 1

    latest_close = float(
        df["close"].iloc[latest_position]
    )

    if latest_close <= level:
        return None

    return {
        "direction": "BUY",
        "broken_level": level,
        "break_index": df.index[
            latest_position
        ],
        "break_position": latest_position,
    }


# ==========================================================
# CURRENT BEARISH BOS
# ==========================================================

def _find_current_bearish_bos(
    df: pd.DataFrame,
    swing_low: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    A bearish BOS is valid only when the LATEST CLOSED
    candle closes below the confirmed swing low.
    """

    level = float(
        swing_low["price"]
    )

    latest_position = len(df) - 1

    latest_close = float(
        df["close"].iloc[latest_position]
    )

    if latest_close >= level:
        return None

    return {
        "direction": "SELL",
        "broken_level": level,
        "break_index": df.index[
            latest_position
        ],
        "break_position": latest_position,
    }


# ==========================================================
# MAIN BOS DETECTOR
# ==========================================================

def detect_h4_bos(
    df: pd.DataFrame,
) -> Dict[str, Any]:

    if not _validate_dataframe(df):
        return no_bos()

    # ------------------------------------------------------
    # Remove currently forming candle.
    # ------------------------------------------------------

    closed = df.iloc[:-1].copy()

    if len(closed) < (
        SWING_LOOKBACK * 2
    ) + 5:

        return no_bos()

    # ------------------------------------------------------
    # Find latest confirmed structures.
    # ------------------------------------------------------

    swing_high = (
        _find_latest_swing_high(
            closed
        )
    )

    swing_low = (
        _find_latest_swing_low(
            closed
        )
    )

    # ------------------------------------------------------
    # If no structures exist, no BOS.
    # ------------------------------------------------------

    if (
        swing_high is None
        and
        swing_low is None
    ):

        return no_bos()

    # ------------------------------------------------------
    # Check CURRENT closed candle only.
    # ------------------------------------------------------

    bullish = None

    bearish = None

    if swing_high is not None:

        bullish = (
            _find_current_bullish_bos(
                closed,
                swing_high,
            )
        )

    if swing_low is not None:

        bearish = (
            _find_current_bearish_bos(
                closed,
                swing_low,
            )
        )

    # ------------------------------------------------------
    # No current BOS.
    # ------------------------------------------------------

    if (
        bullish is None
        and
        bearish is None
    ):

        return no_bos()

    # ------------------------------------------------------
    # Preserve only the relevant current structure.
    # ------------------------------------------------------

    result = no_bos()

    if bullish is not None:

        result["bos"] = True
        result["direction"] = "BUY"
        result["broken_level"] = (
            bullish["broken_level"]
        )
        result["break_index"] = (
            bullish["break_index"]
        )

        if swing_high is not None:

            result["swing_high"] = (
                swing_high["price"]
            )

            result["swing_high_index"] = (
                swing_high["index"]
            )

        return result

    # ------------------------------------------------------
    # Bearish BOS.
    # ------------------------------------------------------

    if bearish is not None:

        result["bos"] = True
        result["direction"] = "SELL"
        result["broken_level"] = (
            bearish["broken_level"]
        )
        result["break_index"] = (
            bearish["break_index"]
        )

        if swing_low is not None:

            result["swing_low"] = (
                swing_low["price"]
            )

            result["swing_low_index"] = (
                swing_low["index"]
            )

        return result

    return no_bos()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "detect_h4_bos",
    "no_bos",
]