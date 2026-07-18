from scanner.symbol_scanner import scan_market


print("=" * 50)
print("MARKET SCANNER TEST")
print("=" * 50)

signals = scan_market()

print()

print(f"Signals Found: {len(signals)}")

for signal in signals:

    print(signal)
