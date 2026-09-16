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
# REAL PRODUCTION-PATH DAILY REVERSAL
#
# Candidate:
#     Bullish Daily Engulfing
#
# Opposing structure:
#     Daily bearish break + retest
#
# Expected:
#     BUY candidate -> SELL reversal
#
# Chronology required by current production implementation:
#
# protected LOW
#       ↓
# structural HIGH
#       ↓
# bearish Daily break
#       ↓
# Daily retest
#       ↓
# bullish Daily engulfing
#       ↓
# SELL
# ============================================================

df = make_daily([
    [105, 110, 102, 106],   # 0
    [106, 108, 100, 104],   # 1 protected LOW
    [104, 125, 103, 120],   # 2 structural HIGH
    [120, 107,  95,  98],   # 3 FULL-BODY bearish break
    [ 98, 103,  94,  99],   # 4 Daily retest
    [ 90, 110,  89, 105],   # 5 bullish engulfing setup
])


# ------------------------------------------------------------
# VERIFY REAL OPPOSING DAILY STRUCTURE
# ------------------------------------------------------------

print("\n=== REAL OPPOSING DAILY BREAK ===")

daily_break = _find_latest_daily_break(
    df,
    "SELL",
    before_index=4,
)

print(daily_break)

assert daily_break is not None
assert daily_break["valid"] is True
assert daily_break["direction"] == "SELL"
assert daily_break["key_level"] == 100.0
assert daily_break["key_level_index"] == 1
assert daily_break["break_index"] == 3


# ------------------------------------------------------------
# VERIFY REAL DAILY RETEST
# ------------------------------------------------------------

print("\n=== REAL DAILY RETEST ===")

retest = detect_break_retest(
    df=df,
    level=100.0,
    direction="SELL",
    level_index=1,
    bos_index=3,
)

print(retest)

assert retest["valid"] is True
assert retest["break_index"] == 3
assert retest["retest_index"] == 4


# ------------------------------------------------------------
# VERIFY ACTUAL PRODUCTION REVERSAL FUNCTION
# ------------------------------------------------------------

print("\n=== PRODUCTION DAILY REVERSAL ===")

daily_setup = {
    "valid": True,
    "direction": "BUY",
    "setup": "BULLISH_ENGULFING",
    "entry": 105.0,
    "setup_candle_index": 5,
}

result = _evaluate_daily_structural_reversal(
    df,
    daily_setup,
)

print(result)

assert result is not None
assert result["valid"] is True
assert result["direction"] == "SELL"
assert result["entry"] == 100.0
assert result["key_level"] == 100.0
assert result["break_index"] == 3
assert result["retest_index"] == 4

print("\nREAL PRODUCTION DAILY REVERSAL TEST: PASSED")
print("BUY engulfing -> Daily bearish break + retest -> SELL")
