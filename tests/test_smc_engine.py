import pandas as pd

from analysis.smc.smc_engine import detect_smc

print("=" * 50)
print("SMC ENGINE TEST")
print("=" * 50)

df = pd.DataFrame({
    "open":  [100, 102, 101, 104, 103],
    "high":  [103, 104, 105, 106, 108],
    "low":   [99, 100, 100, 102, 104],
    "close": [102, 101, 104, 103, 107],
})

result = detect_smc(df)

print(result)

assert "bullish_order_block" in result
assert "bearish_order_block" in result
assert "bullish_fvg" in result
assert "bearish_fvg" in result

print("\nSUCCESS")
