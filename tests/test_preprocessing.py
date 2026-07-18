from data.mexc_api import fetch_ohlcv
from data.validator import validate_data

print("=" * 60)
print("BLISSFINITY AI BOT")
print("PREPROCESSING TEST")
print("=" * 60)

df = fetch_ohlcv(
    "BTC/USDT",
    "4h"
)

print("Downloaded:", len(df), "candles")

validated = validate_data(df)

print("Validated:", len(validated), "candles")

print()
print(validated.tail())

print("\nSUCCESS")
