import pandas as pd

from analysis.liquidity_grab.grab_engine import detect_liquidity_grab

print("=" * 50)
print("LIQUIDITY GRAB TEST")
print("=" * 50)

df = pd.DataFrame({
    "high": [100, 101, 103],
    "low": [98, 99, 98],
    "close": [100, 100, 100]
})

print(detect_liquidity_grab(df))

print("\nSUCCESS")
