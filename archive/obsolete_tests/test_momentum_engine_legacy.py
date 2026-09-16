import pandas as pd

from analysis.momentum.momentum_engine import analyze_momentum

print("=" * 50)
print("MOMENTUM ENGINE TEST")
print("=" * 50)

df = pd.DataFrame({
    "close":[1,2,3,4,5,6,7,8,9,10]
})

result = analyze_momentum(df)

print(result)

assert "momentum" in result

print("\nSUCCESS")
