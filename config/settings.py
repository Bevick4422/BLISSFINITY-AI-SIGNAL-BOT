
"""
BLISSFINITY AI SIGNAL BOT
CONFIGURATION
"""

import ccxt

# ==========================================================
# TELEGRAM
# ==========================================================

TELEGRAM_TOKEN = "8908134517:AAHVTOQdR0f01XDlZfOIvd9yiYNev_t7K-I"
TELEGRAM_CHAT_ID = "-1004459723300"

# ==========================================================
# BOT SETTINGS
# ==========================================================

SCAN_INTERVAL = 60          # Scan every 60 seconds

MIN_DAILY_SIGNALS = 3       # Target signals/day
MAX_DAILY_SIGNALS = 4       # Hard daily limit

MAX_PAIRS = 100             # Scan top 100 futures

# ==========================================================
# MEXC EXCHANGE
# ==========================================================

exchange = ccxt.mexc({
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap"
    }
})

# ==========================================================
# LOAD TOP FUTURES PAIRS
# ==========================================================

def get_symbols():

    exchange.load_markets()
    tickers = exchange.fetch_tickers()

    blacklist = (
        "3L",
        "3S",
        "5L",
        "5S",
        "STOCK",
        "XAU",
        "XAUT",
        "GOLD",
        "SILVER",
        "USOIL",
        "BRENT",
        "WTI",
        "SPX",
        "NASDAQ",
        "DJI",
        "USD1",
        "EUR",
        "GBP",
        "JPY",
    )

    pairs = []

    for symbol, market in exchange.markets.items():

        if not market.get("active", False):
            continue

        if not market.get("swap", False):
            continue

        if market.get("quote") != "USDT":
            continue

        if any(word in symbol.upper() for word in blacklist):
            continue

        ticker = tickers.get(symbol)

        if ticker is None:
            continue

        volume = ticker.get("quoteVolume", 0) or 0

        pairs.append((symbol, volume))

    pairs.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [symbol for symbol, _ in pairs[:MAX_PAIRS]]

# ==========================================================
# SYMBOLS
# ==========================================================

SYMBOLS = get_symbols()

# ==========================================================
# STARTUP INFO
# ==========================================================

print("=" * 60)
print("BLISSFINITY AI SIGNAL BOT")
print("=" * 60)
print(f"Loaded {len(SYMBOLS)} Futures Pairs")
print(f"Scan Interval      : {SCAN_INTERVAL}s")
print(f"Daily Signals      : {MIN_DAILY_SIGNALS}-{MAX_DAILY_SIGNALS}")
print(f"Pairs Scanned      : {MAX_PAIRS}")
print("=" * 60)