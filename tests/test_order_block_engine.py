import pandas as pd

from analysis.order_block.order_block_engine import detect_order_block

print("=" * 50)
print("ORDER BLOCK ENGINE TEST")
print("=" * 50)

df = pd.DataFrame({

    "open":  [100,101,102,103,102],
    "high":  [101,102,103,104,106],
    "low":   [99,100,101,100,101],
    "close": [101,102,101,101,105]

})

print(detect_order_block(df))

print("\nSUCCESS")
