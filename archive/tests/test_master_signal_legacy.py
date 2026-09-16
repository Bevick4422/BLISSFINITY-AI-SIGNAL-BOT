from market_data.mexc_client import get_klines
from signals.master_signal_engine import build_master_signal

print("=" * 50)
print("MASTER SIGNAL TEST")
print("=" * 50)

df = get_klines("BTC_USDT", "Min15", limit=300)

result = build_master_signal(df)

print(result)

print("\nSUCCESS")
