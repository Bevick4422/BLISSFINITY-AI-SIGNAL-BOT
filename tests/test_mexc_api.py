from data.mexc_api import fetch_ohlcv

print("=" * 60)
print("BLISSFINITY AI BOT")
print("Testing MEXC API")
print("=" * 60)

df = fetch_ohlcv(
    "BTC/USDT",
    "4h"
)

print(df.tail())

print("\nSUCCESS")
