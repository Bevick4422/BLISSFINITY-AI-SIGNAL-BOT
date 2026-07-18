from market_data.mexc_client import get_klines

print("=" * 50)
print("MEXC CLIENT TEST")
print("=" * 50)

df = get_klines(
    symbol="BTC_USDT",
    interval="15m",
    limit=10,
)

print(df.tail())
print()
print("SUCCESS")
