from data.mexc_api import fetch_ohlcv
from data.validator import validate_data
from analysis.market_regime import detect_market_regime

print("=" * 60)
print("MARKET REGIME TEST")
print("=" * 60)

df = fetch_ohlcv("BTC/USDT", "4h")

df = validate_data(df)

regime = detect_market_regime(df)

print()

print("Market Regime:")

print(regime)

print()

print("SUCCESS")
