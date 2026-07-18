from scanner.market_scanner import fetch_market_data
from analysis.fvg.fvg_engine import detect_fvg

print("=" * 50)
print("FVG ENGINE TEST")
print("=" * 50)

df = fetch_market_data("BTC/USDT")

result = detect_fvg(df)

print(result)

print()
print("SUCCESS")
