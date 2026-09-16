import pandas as pd

from analysis.smt.smt_engine import detect_smt_divergence

print("=" * 50)
print("SMT TEST")
print("=" * 50)

btc = pd.DataFrame({
    "high": [100,102,104,105,108],
    "low":  [95,96,97,98,99]
})

eth = pd.DataFrame({
    "high": [90,91,92,93,93],
    "low":  [80,81,82,83,84]
})

print(detect_smt_divergence(btc, eth))

print("\nSUCCESS")
