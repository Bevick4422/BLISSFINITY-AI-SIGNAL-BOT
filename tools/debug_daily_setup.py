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


rows = [
    [90, 93, 88, 91, 1000],
    [91, 96, 89, 94, 1000],
    [94, 99, 92, 97, 1000],
    [97, 102, 95, 100, 1000],
    [100, 105, 98, 103, 1000],
    [103, 108, 101, 106, 1000],
    [106, 110, 103, 108, 1000],
    [107, 111, 102, 110, 1000],
    [109, 112, 104, 105, 1000],
    [104, 113, 103, 112, 1000],
]

df = make_df(rows)

result = detect_daily_setup(df)

print()
print("=" * 60)
print("RUNTIME DAILY SETUP DIAGNOSTIC")
print("=" * 60)

print("TYPE:", type(result))
print("RESULT:")
print(result)

print()
print("KEY FIELDS:")
print("setup              :", result.get("setup"))
print("direction          :", result.get("direction"))
print("entry              :", result.get("entry"))
print("level              :", result.get("level"))
print("level_index        :", result.get("level_index"))
print("setup_candle_index :", result.get("setup_candle_index"))
print("setup_candle_time  :", result.get("setup_candle_timestamp"))
print("=" * 60)