import ccxt

exchange = ccxt.mexc({
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap"
    }
})

markets = exchange.load_markets()

print("Total Markets:", len(markets))

count = 0

for symbol, market in markets.items():
    if market.get("swap", False):
        print(symbol)
        count += 1

print("\nTotal Swap Markets:", count)