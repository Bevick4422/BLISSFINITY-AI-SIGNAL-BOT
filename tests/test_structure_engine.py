import pandas as pd

from analysis.structure.structure_engine import detect_structure


df = pd.DataFrame({
    "high": [10,11,12,13,14,15,16,17,18,19],
    "low": [5,6,7,8,9,10,11,12,13,14]
})

result = detect_structure(df)

print("="*50)
print("STRUCTURE ENGINE TEST")
print("="*50)

print(result)

assert "trend_structure" in result
assert "bos" in result
assert "choch" in result

print("\nSUCCESS")
