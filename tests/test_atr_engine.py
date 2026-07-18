from scanner.market_scanner import fetch_market_data
from analysis.atr.atr_engine import calculate_atr

print("=" * 50)
print("ATR ENGINE TEST")
print("=" * 50)

df = fetch_market_data("BTC/USDT")

atr = calculate_atr(df)

print(f"ATR = {atr}")

print()
print("SUCCESS")
