from market_data.symbol_fetcher import get_all_symbols

print("=" * 50)
print("MEXC SYMBOL FETCHER TEST")
print("=" * 50)

symbols = get_all_symbols()

print(f"Total Symbols: {len(symbols)}")
print()

print(symbols[:30])
