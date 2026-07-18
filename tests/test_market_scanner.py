from scanner.market_scanner import fetch_market_data

print("="*50)
print("MARKET SCANNER TEST")
print("="*50)

df = fetch_market_data()

print(df.tail())

assert len(df) > 100

print("\nSUCCESS")
