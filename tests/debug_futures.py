import ccxt

exchange = ccxt.mexc({
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap"
    }
})

markets = exchange.load_markets()

count = 0

for symbol, market in markets.items():

    print(
        symbol,
        "|",
        market.get("type"),
        "|",
        market.get("spot"),
        "|",
        market.get("swap"),
        "|",
        market.get("future"),
        "|",
        market.get("quote")
    )

    count += 1

    if count == 30:
        break