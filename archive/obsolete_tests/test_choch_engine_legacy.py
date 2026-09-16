"""
BLISSFINITY SIGNAL
CHOCH ENGINE CONTROLLED TESTS

Tests the locked CHOCH rules:

BEARISH CHOCH
- Identify a protected structural LOW.
- The protected low is the low that created the prior structural high.
- That protected low must be broken.
- The break must occur with a completed BEARISH ENGULFING candle.
- Direction change itself is sufficient.
- Retest is OPTIONAL.

BULLISH CHOCH
- Identify a protected structural HIGH.
- The protected high is the high that created the prior structural low.
- That protected high must be broken.
- The break must occur with a completed BULLISH ENGULFING candle.
- Direction change itself is sufficient.
- Retest is OPTIONAL.

Wicks do not qualify as the structural break.
Only completed candles are used.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------
# IMPORT CHOCH ENGINE
# ---------------------------------------------------------------------

try:
    from analysis.choch.choch_engine import detect_choch
except ImportError:
    try:
        from analysis.choch_engine import detect_choch
    except ImportError:
        detect_choch = None


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def make_df(rows):
    index = pd.date_range(
        "2026-01-01",
        periods=len(rows),
        freq="4h",
        tz="UTC",
    )

    return pd.DataFrame(
        rows,
        index=index,
        columns=["open", "high", "low", "close", "volume"],
    )


def require_engine():
    assert detect_choch is not None, (
        "CHOCH engine could not be imported. "
        "Expected analysis.choch.choch_engine.detect_choch"
    )


# ---------------------------------------------------------------------
# BEARISH CHOCH FIXTURE
# ---------------------------------------------------------------------

def bearish_choch_data():
    """
    Structure:

        High
          |
    protected LOW
          |
        rally
          |
    bearish engulfing breaks protected LOW

    The protected low is the low that created the prior high.

    Final candle:
    - bearish
    - body engulfs previous bullish body
    - closes below protected low
    """

    rows = [
        # 0
        [100, 104, 98, 103, 1000],

        # 1 - swing high
        [103, 112, 102, 110, 1000],

        # 2 - protected low that created the high
        [110, 111, 104, 106, 1000],

        # 3
        [106, 114, 105, 112, 1000],

        # 4
        [112, 116, 109, 115, 1000],

        # 5 - bullish candle immediately before CHOCH
        [115, 118, 111, 117, 1000],

        # 6 - bearish engulfing CHOCH
        #
        # Body: 119 -> 102
        # Previous body: 115 -> 117
        # Engulfs previous bullish body.
        # Close is below protected low 104.
        [119, 120, 101, 102, 1000],
    ]

    return make_df(rows)


# ---------------------------------------------------------------------
# BULLISH CHOCH FIXTURE
# ---------------------------------------------------------------------

def bullish_choch_data():
    """
    Structure:

        Low
          |
    protected HIGH
          |
       decline
          |
    bullish engulfing breaks protected HIGH

    The protected high is the high that created the prior low.

    Final candle:
    - bullish
    - body engulfs previous bearish body
    - closes above protected high
    """

    rows = [
        # 0
        [110, 112, 105, 107, 1000],

        # 1 - swing low
        [107, 108, 98, 100, 1000],

        # 2 - protected high that created the low
        [100, 106, 99, 104, 1000],

        # 3
        [104, 105, 94, 96, 1000],

        # 4
        [96, 99, 90, 92, 1000],

        # 5 - bearish candle immediately before CHOCH
        [92, 94, 86, 88, 1000],

        # 6 - bullish engulfing CHOCH
        #
        # Body: 84 -> 108
        # Previous body: 92 -> 88
        # Engulfs previous bearish body.
        # Close is above protected high 106.
        [84, 110, 83, 108, 1000],
    ]

    return make_df(rows)


# ---------------------------------------------------------------------
# NEGATIVE: BEARISH WICK ONLY
# ---------------------------------------------------------------------

def bearish_wick_only_data():
    rows = [
        [100, 104, 98, 103, 1000],
        [103, 112, 102, 110, 1000],
        [110, 111, 104, 106, 1000],
        [106, 114, 105, 112, 1000],
        [112, 116, 109, 115, 1000],
        [115, 118, 111, 117, 1000],

        # Wick penetrates protected low 104,
        # but candle body closes above it.
        [108, 110, 103, 106, 1000],
    ]

    return make_df(rows)


# ---------------------------------------------------------------------
# NEGATIVE: BULLISH WICK ONLY
# ---------------------------------------------------------------------

def bullish_wick_only_data():
    rows = [
        [110, 112, 105, 107, 1000],
        [107, 108, 98, 100, 1000],
        [100, 106, 99, 104, 1000],
        [104, 105, 94, 96, 1000],
        [96, 99, 90, 92, 1000],
        [92, 94, 86, 88, 1000],

        # Wick penetrates protected high 106,
        # but candle body closes below it.
        [104, 110, 102, 105, 1000],
    ]

    return make_df(rows)


# ---------------------------------------------------------------------
# NEGATIVE: WRONG CANDLE TYPE
# ---------------------------------------------------------------------

def bearish_break_without_bearish_engulfing():
    rows = [
        [100, 104, 98, 103, 1000],
        [103, 112, 102, 110, 1000],
        [110, 111, 104, 106, 1000],
        [106, 114, 105, 112, 1000],
        [112, 116, 109, 115, 1000],
        [115, 118, 111, 117, 1000],

        # Breaks below protected low,
        # but does NOT engulf previous bullish body.
        [116, 117, 100, 105, 1000],
    ]

    return make_df(rows)


def bullish_break_without_bullish_engulfing():
    rows = [
        [110, 112, 105, 107, 1000],
        [107, 108, 98, 100, 1000],
        [100, 106, 99, 104, 1000],
        [104, 105, 94, 96, 1000],
        [96, 99, 90, 92, 1000],
        [92, 94, 86, 88, 1000],

        # Breaks above protected high,
        # but does NOT engulf previous bearish body.
        [90, 110, 89, 105, 1000],
    ]

    return make_df(rows)


# ---------------------------------------------------------------------
# TEST HELPERS
# ---------------------------------------------------------------------

def run_engine(df):
    require_engine()

    result = detect_choch(df)

    assert result is not None, "CHOCH engine returned None."

    return result


# ---------------------------------------------------------------------
# TEST 1
# ---------------------------------------------------------------------

def test_bearish_choch_detected():
    result = run_engine(bearish_choch_data())

    assert result["valid"] is True
    assert result["direction"] == "SELL"

    print("\nPASS: bearish CHOCH detected")
    print(result)


# ---------------------------------------------------------------------
# TEST 2
# ---------------------------------------------------------------------

def test_bullish_choch_detected():
    result = run_engine(bullish_choch_data())

    assert result["valid"] is True
    assert result["direction"] == "BUY"

    print("\nPASS: bullish CHOCH detected")
    print(result)


# ---------------------------------------------------------------------
# TEST 3
# ---------------------------------------------------------------------

def test_bearish_wick_only_rejected():
    result = run_engine(bearish_wick_only_data())

    assert result["valid"] is False

    print("\nPASS: bearish wick-only break rejected")
    print(result)


# ---------------------------------------------------------------------
# TEST 4
# ---------------------------------------------------------------------

def test_bullish_wick_only_rejected():
    result = run_engine(bullish_wick_only_data())

    assert result["valid"] is False

    print("\nPASS: bullish wick-only break rejected")
    print(result)


# ---------------------------------------------------------------------
# TEST 5
# ---------------------------------------------------------------------

def test_bearish_wrong_candle_type_rejected():
    result = run_engine(
        bearish_break_without_bearish_engulfing()
    )

    assert result["valid"] is False

    print("\nPASS: bearish non-engulfing break rejected")
    print(result)


# ---------------------------------------------------------------------
# TEST 6
# ---------------------------------------------------------------------

def test_bullish_wrong_candle_type_rejected():
    result = run_engine(
        bullish_break_without_bullish_engulfing()
    )

    assert result["valid"] is False

    print("\nPASS: bullish non-engulfing break rejected")
    print(result)