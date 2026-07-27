import ccxt

exchange = ccxt.mexc({
    "enableRateLimit": True
})

exchange.load_markets()

count = 0

for symbol, market in exchange.markets.items():
    if market.get("swap"):
        count += 1
        print(symbol)

print()
print("Total swap markets:", count)