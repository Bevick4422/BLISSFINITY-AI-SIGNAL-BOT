from data.mexc_api import fetch_ohlcv
from data.preprocessing.validator import validate_data
from analysis.trend.trend_engine import detect_trend

print("=" * 60)
print("TREND ENGINE TEST")
print("=" * 60)

df = fetch_ohlcv("BTC/USDT", "4h")

df = validate_data(df)

trend = detect_trend(df)

print()

print("Detected Trend:")
print(trend)

print()

print("SUCCESS")
