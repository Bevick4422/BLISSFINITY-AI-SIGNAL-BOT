"""
BLISSFINITY SIGNAL
Controlled tests for additional entry modules.

Modules tested:
- CHOCH
- Fresh Level
- Left Shoulder
- Rejection

No exchange/API/network calls.
All candles are treated as completed H4 candles.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.entry.choch import detect_choch
from analysis.entry.fresh_level import detect_fresh_level
from analysis.entry.left_shoulder import detect_left_shoulder
from analysis.rejection.rejection_engine import (
    bullish_rejection,
    bearish_rejection,
)


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


# ============================================================
# CHOCH
# ============================================================

def bullish_choch_df():
    return make_df(
        [
            [100, 105, 98, 104, 1000],
            [104, 108, 102, 106, 1000],
            [106, 110, 103, 108, 1000],
            [108, 111, 104, 107, 1000],

            # Previous bearish candle
            [107, 109, 101, 103, 1000],

            # Bullish engulfing breaks protected HIGH = 106
            [103, 112, 102, 110, 1000],
        ]
    )


def test_bullish_choch():
    df = bullish_choch_df()

    result = detect_choch(
        df=df,
        protected_level=106.0,
        direction="BUY",
        protected_index=3,
    )

    assert result["valid"] is True
    assert result["direction"] == "BUY"
    assert result["entry_type"] == "CHOCH_CLOSE"
    assert result["entry"] == 110.0
    assert result["choch_index"] == 5
    assert result["stop_reference"]["type"] == "PROTECTED_STRUCTURE_WICK"

    print("PASS: bullish CHOCH")


def bearish_choch_df():
    return make_df(
        [
            [110, 112, 105, 108, 1000],
            [108, 111, 104, 106, 1000],
            [106, 109, 102, 105, 1000],
            [105, 108, 101, 103, 1000],

            # Previous bullish candle
            [103, 110, 102, 108, 1000],

            # Bearish engulfing breaks protected LOW = 104
            [108, 109, 98, 100, 1000],
        ]
    )


def test_bearish_choch():
    df = bearish_choch_df()

    result = detect_choch(
        df=df,
        protected_level=104.0,
        direction="SELL",
        protected_index=3,
    )

    assert result["valid"] is True
    assert result["direction"] == "SELL"
    assert result["entry_type"] == "CHOCH_CLOSE"
    assert result["entry"] == 100.0
    assert result["choch_index"] == 5
    assert result["stop_reference"]["type"] == "PROTECTED_STRUCTURE_WICK"

    print("PASS: bearish CHOCH")


def test_choch_wrong_candle_no_signal():
    df = make_df(
        [
            [100, 105, 98, 104, 1000],
            [104, 108, 102, 106, 1000],
            [106, 110, 103, 108, 1000],
            [108, 111, 104, 107, 1000],

            # Red candle does not bullish-engulf
            [107, 109, 101, 103, 1000],

            # Breaks level but does not engulf previous body
            [103, 112, 102, 107, 1000],
        ]
    )

    result = detect_choch(
        df=df,
        protected_level=106.0,
        direction="BUY",
        protected_index=3,
    )

    assert result["valid"] is False

    print("PASS: CHOCH invalid candle rejected")


# ============================================================
# FRESH LEVEL
# ============================================================

def test_fresh_level_buy():
    df = make_df(
        [
            [100, 105, 95, 103, 1000],
            [103, 110, 100, 108, 1000],
            [108, 112, 102, 110, 1000],

            # Creation candle for Demand level = 100
            [110, 113, 99, 105, 1000],

            # Does not touch 100
            [105, 112, 103, 109, 1000],

            # First later touch
            [109, 111, 98, 106, 1000],
        ]
    )

    result = detect_fresh_level(
        df=df,
        level=100.0,
        direction="BUY",
        level_index=3,
        trend="BULLISH",
    )

    assert result["valid"] is True
    assert result["entry_type"] == "FRESH_LEVEL"
    assert result["entry"] == 100.0
    assert result["touch_index"] == 5
    assert result["stop_reference"]["type"] == "ESTABLISHING_CANDLE_WICK"

    print("PASS: Fresh Level BUY")


def test_fresh_level_already_mitigated():
    df = make_df(
        [
            [100, 105, 95, 103, 1000],
            [103, 110, 100, 108, 1000],
            [108, 112, 102, 110, 1000],

            # Level creation
            [110, 113, 99, 105, 1000],

            # Touch destroys freshness
            [105, 108, 98, 101, 1000],

            # Price moves away
            [101, 110, 102, 108, 1000],
        ]
    )

    result = detect_fresh_level(
        df=df,
        level=100.0,
        direction="BUY",
        level_index=3,
        trend="BULLISH",
    )

    assert result["valid"] is True
    assert result["touch_index"] == 4

    print("PASS: Fresh Level first-touch detection")


def test_fresh_level_wrong_trend_rejected():
    df = make_df(
        [
            [100, 105, 95, 103, 1000],
            [103, 110, 100, 108, 1000],
            [108, 112, 102, 110, 1000],
            [110, 113, 99, 105, 1000],
            [105, 112, 103, 109, 1000],
            [109, 111, 98, 106, 1000],
        ]
    )

    result = detect_fresh_level(
        df=df,
        level=100.0,
        direction="BUY",
        level_index=3,
        trend="BEARISH",
    )

    assert result["valid"] is False

    print("PASS: Fresh Level wrong trend rejected")


# ============================================================
# LEFT SHOULDER
# ============================================================

def bullish_left_shoulder_df():
    return make_df(
        [
            # Break #1
            [99, 103, 98, 102, 1000],

            # Pullback toward level
            [102, 103, 99, 100, 1000],

            # Break #2
            [100, 106, 100, 105, 1000],

            # Apex / higher low for BUY
            [105, 108, 103, 106, 1000],

            # Move away
            [106, 110, 105, 109, 1000],

            # Final retrace to level
            [109, 110, 99, 102, 1000],
        ]
    )


def test_bullish_left_shoulder():
    df = bullish_left_shoulder_df()

    result = detect_left_shoulder(
        df=df,
        level=100.0,
        direction="BUY",
    )

    assert result["valid"] is True
    assert result["entry_type"] == "LEFT_SHOULDER"
    assert result["broken_level"] == 100.0
    assert result["break1_index"] == 0
    assert result["break2_index"] == 2
    assert result["apex_index"] == 3
    assert result["retest_index"] == 5
    assert result["stop_reference"]["type"] == "APEX"

    print("PASS: bullish Left Shoulder")


def bearish_left_shoulder_df():
    return make_df(
        [
            # Break #1
            [101, 102, 96, 98, 1000],

            # Pullback toward level
            [98, 101, 97, 100, 1000],

            # Break #2
            [100, 101, 94, 95, 1000],

            # Apex / lower high for SELL
            [95, 97, 93, 94, 1000],

            # Move away
            [94, 96, 90, 91, 1000],

            # Final retrace to level
            [91, 102, 90, 96, 1000],
        ]
    )


def test_bearish_left_shoulder():
    df = bearish_left_shoulder_df()

    result = detect_left_shoulder(
        df=df,
        level=100.0,
        direction="SELL",
    )

    assert result["valid"] is True
    assert result["entry_type"] == "LEFT_SHOULDER"
    assert result["broken_level"] == 100.0
    assert result["break1_index"] == 0
    assert result["break2_index"] == 2
    assert result["apex_index"] == 3
    assert result["retest_index"] == 5
    assert result["stop_reference"]["type"] == "APEX"

    print("PASS: bearish Left Shoulder")


def test_left_shoulder_incomplete_rejected():
    df = make_df(
        [
            [99, 103, 98, 102, 1000],
            [102, 103, 99, 100, 1000],
            [100, 106, 100, 105, 1000],
        ]
    )

    result = detect_left_shoulder(
        df=df,
        level=100.0,
        direction="BUY",
    )

    assert result["valid"] is False

    print("PASS: incomplete Left Shoulder rejected")


# ============================================================
# REJECTION
# ============================================================

def test_bullish_rejection():
    candle = pd.Series(
        {
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 103.0,
            "volume": 1000.0,
        }
    )

    assert bullish_rejection(candle, 100.0) is True

    print("PASS: bullish rejection")


def test_bearish_rejection():
    candle = pd.Series(
        {
            "open": 103.0,
            "high": 105.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000.0,
        }
    )

    assert bearish_rejection(candle, 100.0) is True

    print("PASS: bearish rejection")


def test_rejection_wrong_direction_rejected():
    candle = pd.Series(
        {
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 103.0,
            "volume": 1000.0,
        }
    )

    assert bearish_rejection(candle, 100.0) is False

    print("PASS: rejection wrong direction rejected")


# ============================================================
# RUN SUMMARY
# ============================================================

if __name__ == "__main__":
    tests = [
        test_bullish_choch,
        test_bearish_choch,
        test_choch_wrong_candle_no_signal,
        test_fresh_level_buy,
        test_fresh_level_already_mitigated,
        test_fresh_level_wrong_trend_rejected,
        test_bullish_left_shoulder,
        test_bearish_left_shoulder,
        test_left_shoulder_incomplete_rejected,
        test_bullish_rejection,
        test_bearish_rejection,
        test_rejection_wrong_direction_rejected,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print()
    print(f"{passed}/{len(tests)} ENTRY MODULE TESTS PASSED")