from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from engine.strategy_engine import (
    _evaluate_daily_structural_reversal,
    _find_latest_daily_break,
)
from analysis.entry.break_retest import detect_break_retest


def make_daily(rows):
    index = pd.date_range(
        "2026-01-01",
        periods=len(rows),
        freq="D",
        tz="UTC",
    )

    return pd.DataFrame(
        rows,
        index=index,
        columns=["open", "high", "low", "close"],
    )


# ============================================================
# TEST 1
# BUY ENGULFING -> DAILY BEARISH BREAK + RETEST -> SELL
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: BUY -> SELL")
print("=" * 70)

df1 = make_daily([
    [105, 110, 102, 106],
    [106, 108, 100, 104],
    [104, 125, 103, 120],
    [120, 107,  95,  98],
    [ 98, 103,  94,  99],
    [ 90, 110,  89, 105],
])

result1 = _evaluate_daily_structural_reversal(
    df1,
    {
        "valid": True,
        "direction": "BUY",
        "setup": "BULLISH_ENGULFING",
        "entry": 105.0,
        "setup_candle_index": 5,
    },
)

print("\nRESULT:")
print(result1)

assert result1 is not None
assert result1["valid"] is True
assert result1["direction"] == "SELL"
assert result1["key_level"] == 100.0
assert result1["break_index"] == 3
assert result1["retest_index"] == 4

print("\nTEST 1 PASSED")


# ============================================================
# TEST 2
# SELL ENGULFING -> DAILY BULLISH BREAK + RETEST -> BUY
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: SELL -> BUY")
print("=" * 70)

df2 = make_daily([
    [ 95,  98,  90,  92],
    [ 92, 100,  89,  95],
    [ 95,  96,  75,  80],
    [ 80, 102,  78, 101],
    [101, 106,  99, 104],
    [110, 112,  88,  90],
])

daily_break2 = _find_latest_daily_break(
    df2,
    "BUY",
    before_index=4,
)

print("\nREAL BULLISH DAILY BREAK:")
print(daily_break2)

assert daily_break2 is not None
assert daily_break2["valid"] is True
assert daily_break2["direction"] == "BUY"
assert daily_break2["key_level"] == 100.0
assert daily_break2["key_level_index"] == 1
assert daily_break2["break_index"] == 3

retest2 = detect_break_retest(
    df=df2,
    level=100.0,
    direction="BUY",
    level_index=1,
    bos_index=3,
)

print("\nREAL DAILY RETEST:")
print(retest2)

assert retest2["valid"] is True
assert retest2["break_index"] == 3
assert retest2["retest_index"] == 4

result2 = _evaluate_daily_structural_reversal(
    df2,
    {
        "valid": True,
        "direction": "SELL",
        "setup": "BEARISH_ENGULFING",
        "entry": 90.0,
        "setup_candle_index": 5,
    },
)

print("\nRESULT:")
print(result2)

assert result2 is not None
assert result2["valid"] is True
assert result2["direction"] == "BUY"
assert result2["key_level"] == 100.0
assert result2["break_index"] == 3
assert result2["retest_index"] == 4

print("\nTEST 2 PASSED")


# ============================================================
# TEST 3
# BUY ENGULFING -> BEARISH BREAK -> NO RETEST -> BUY SURVIVES
#
# IMPORTANT:
# The bullish engulfing candle remains entirely ABOVE 100.
# Therefore it cannot become a later retest.
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: NO RETEST -> ORIGINAL BUY SURVIVES")
print("=" * 70)

df3 = make_daily([
    [105, 110, 102, 106],   # 0
    [106, 108, 100, 104],   # 1 protected LOW
    [104, 125, 103, 120],   # 2 structural HIGH
    [120, 107,  95,  98],   # 3 bearish full-body break
    [ 90,  95,  85,  92],   # 4 NO retest of 100
    [103, 106, 101, 105],   # 5 bullish engulfing, entirely > 100
])

daily_break3 = _find_latest_daily_break(
    df3,
    "SELL",
    before_index=4,
)

print("\nREAL BEARISH DAILY BREAK:")
print(daily_break3)

assert daily_break3 is not None
assert daily_break3["valid"] is True
assert daily_break3["direction"] == "SELL"
assert daily_break3["key_level"] == 100.0
assert daily_break3["break_index"] == 3

retest3 = detect_break_retest(
    df=df3,
    level=100.0,
    direction="SELL",
    level_index=1,
    bos_index=3,
)

print("\nREAL DAILY RETEST:")
print(retest3)

assert retest3["valid"] is not True

result3 = _evaluate_daily_structural_reversal(
    df3,
    {
        "valid": True,
        "direction": "BUY",
        "setup": "BULLISH_ENGULFING",
        "entry": 105.0,
        "setup_candle_index": 5,
    },
)

print("\nRESULT:")
print(result3)

assert result3 is None

print("\nTEST 3 PASSED")


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("REAL DAILY REVERSAL SUITE: PASSED")
print("=" * 70)
print("TEST 1: BUY -> SELL reversal with Daily break + retest  PASS")
print("TEST 2: SELL -> BUY reversal with Daily break + retest  PASS")
print("TEST 3: No retest -> original direction survives       PASS")
print("=" * 70)
