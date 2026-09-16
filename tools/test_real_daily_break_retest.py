from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

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


# ------------------------------------------------------------
# REAL DAILY BEARISH BREAK + RETEST
#
# Protected LOW / broken level = 100
#
# Candle 3:
#   open  = 120
#   close = 98
#
# Full-body bearish break below 100:
#   body crosses 100 and closes below it.
#
# Candle 4:
#   low = 94
#   high = 103
#
# Price returns through 100 -> valid retest.
# ------------------------------------------------------------

df = make_daily([
    [105, 110, 102, 106],   # 0
    [106, 108, 100, 104],   # 1 protected LOW
    [104, 125, 103, 120],   # 2 structural HIGH
    [120, 107,  95,  98],   # 3 FULL-BODY bearish break
    [ 98, 103,  94,  99],   # 4 retest of 100
])


BROKEN_LEVEL = 100.0
BOS_INDEX = 3
LEVEL_INDEX = 1


print("\n=== REAL DAILY BEARISH BREAK + RETEST ===")

retest = detect_break_retest(
    df,
    level=BROKEN_LEVEL,
    direction="SELL",
    level_index=LEVEL_INDEX,
    bos_index=BOS_INDEX,
)

print(retest)

assert retest["valid"] is True
assert retest["entry_type"] == "BREAK_RETEST"
assert retest["direction"] if "direction" in retest else True
assert retest["break_index"] == BOS_INDEX
assert retest["retest_index"] == 4
assert retest["broken_level"] == BROKEN_LEVEL
assert retest["stop_reference"]["level_index"] == LEVEL_INDEX


print("\nREAL DAILY BREAK + RETEST TEST: PASSED")
