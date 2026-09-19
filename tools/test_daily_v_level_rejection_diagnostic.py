import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.daily_structure.daily_structure_engine import detect_daily_setup


def make_df(rows):
    idx = pd.date_range(
        "2026-01-01",
        periods=len(rows),
        freq="D",
        tz="UTC",
    )
    return pd.DataFrame(
        rows,
        index=idx,
        columns=["open", "high", "low", "close", "volume"],
    )


# Synthetic sequence:
# - Establish a V-shaped red-to-green level.
# - Later candles sell down toward that prior level.
# - The final candle closes bullish with a lower-wick rejection.
# - Candles are deliberately kept separate from the earlier
#   bullish-engulfing example.
rows = [
    [100, 104,  98, 102, 1000],
    [102, 106, 100, 104, 1000],
    [104, 108, 102, 106, 1000],
    [106, 109, 101, 102, 1000],  # red leg
    [102, 107, 100, 105, 1000],  # green leg: candidate V
    [105, 110, 104, 108, 1000],
    [108, 112, 106, 110, 1000],
    [110, 111, 103, 105, 1000],  # sell-off
    [105, 108, 101, 103, 1000],  # approaches prior V area
    [103, 107, 100, 106, 1000],  # bullish close / lower wick
]

df = make_df(rows)
result = detect_daily_setup(df)

print("\n" + "=" * 64)
print("READ-ONLY DAILY V-LEVEL REJECTION DIAGNOSTIC")
print("=" * 64)
print("Candidate prior V pair: index 3 -> index 4")
print("Candidate V level (green candle open):", rows[4][0])
print("Final candle: index", len(rows) - 1)
print("Final candle OHLC:", rows[-1][:4])
print("\nDETECTOR RESULT:")
print(result)

print("\nKEY FIELDS:")
for key in (
    "valid",
    "trend",
    "setup",
    "direction",
    "level",
    "level_index",
    "setup_candle_index",
    "setup_candle_timestamp",
    "entry",
    "retest_required",
    "entry_mode",
    "reason",
):
    print(f"{key:26}: {result.get(key)}")

print("=" * 64)
