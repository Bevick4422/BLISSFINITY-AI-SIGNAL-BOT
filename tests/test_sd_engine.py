import pandas as pd

from analysis.supply_demand.sd_engine import detect_supply_demand

print("=" * 50)
print("SUPPLY DEMAND TEST")
print("=" * 50)

df = pd.DataFrame({
    "high":[10,11,12,13,14,15,16,17,18,19,
            20,21,22,23,24,25,26,27,28,29],
    "low":[5,5,6,6,7,7,8,8,9,9,
           10,10,11,11,12,12,13,13,14,14],
    "close":[15]*20
})

result = detect_supply_demand(df)

print(result)

assert "bias" in result

print("\nSUCCESS")
