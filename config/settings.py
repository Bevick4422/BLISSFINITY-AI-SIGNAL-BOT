"""
BLISSFINITY SIGNAL BOT
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

SCAN_INTERVAL = 60          # Seconds
MIN_DAILY_SIGNALS = 3
MAX_DAILY_SIGNALS = 4
MAX_PAIRS = 100

# ==========================================================
# MEXC FUTURES
# ==========================================================

exchange = ccxt.mexc(
    {
        "enableRateLimit": True,
        "options": {
            "defaultType": "swap",
        },
    }
)

# ==========================================================
# LOAD CRYPTO FUTURES
# ==========================================================

def get_symbols():
    """
    Load the highest-volume MEXC USDT perpetual
    cryptocurrency futures only.
    """

    print("Loading MEXC futures markets...")

    exchange.load_markets()
    tickers = exchange.fetch_tickers()

    crypto_pairs = []

    for symbol, market in exchange.markets.items():

        # Only active markets
        if not market.get("active", False):
            continue

        # Only perpetual futures
        if not market.get("swap", False):
            continue

        # USDT quoted only
        if market.get("quote") != "USDT":
            continue

        # Must have a crypto base asset
        base = market.get("base")
        if not base:
            continue

        # Skip leveraged tokens
        if base.endswith(("3L", "3S", "5L", "5S")):
            continue

        # Ignore symbols with missing ticker data
        ticker = tickers.get(symbol)
        if ticker is None:
            continue

        volume = ticker.get("quoteVolume") or 0

        crypto_pairs.append(
            (
                symbol,
                volume,
            )
        )

    crypto_pairs.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    selected = [
        symbol
        for symbol, _ in crypto_pairs[:MAX_PAIRS]
    ]

    print(f"Loaded {len(selected)} crypto futures pairs.")

    return selected


# ==========================================================
# SYMBOL LIST
# ==========================================================

SYMBOLS = get_symbols()

# ==========================================================
# STARTUP
# ==========================================================

print("=" * 60)
print("BLISSFINITY SIGNAL BOT")
print("=" * 60)
print(f"Pairs Loaded       : {len(SYMBOLS)}")
print(f"Pairs Scanned      : {MAX_PAIRS}")
print(f"Scan Interval      : {SCAN_INTERVAL} seconds")
print(f"Daily Signals      : {MIN_DAILY_SIGNALS}-{MAX_DAILY_SIGNALS}")
print("=" * 60)