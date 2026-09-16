import pandas as pd

from analysis.premium_discount.premium_discount_engine import detect_premium_discount

print("=" * 50)
print("PREMIUM / DISCOUNT TEST")
print("=" * 50)

df = pd.DataFrame({

    "high": [120,121,122,123,124],
    "low": [100,101,102,103,104],
    "close": [105,106,107,108,109]

})

print(detect_premium_discount(df))

print("\nSUCCESS")
