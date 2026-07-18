from scanner.market_scanner import fetch_market_data
from analysis.volume.volume_engine import detect_volume

print("=" * 50)
print("VOLUME ENGINE TEST")
print("=" * 50)

df = fetch_market_data("BTC/USDT")

result = detect_volume(df)

print(result)

print("\nSUCCESS")
