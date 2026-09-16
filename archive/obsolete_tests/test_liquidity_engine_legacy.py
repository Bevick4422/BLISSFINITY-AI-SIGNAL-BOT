import pandas as pd

from analysis.liquidity.liquidity_engine import detect_liquidity

df = pd.DataFrame({
    "high":[10,11,12,13,14,15,16,18],
    "low":[5,6,7,8,9,10,11,4]
})

result = detect_liquidity(df)

print("="*50)
print("LIQUIDITY ENGINE TEST")
print("="*50)

print(result)

assert "liquidity_sweep_high" in result
assert "liquidity_sweep_low" in result
print("\nSUCCESS")
