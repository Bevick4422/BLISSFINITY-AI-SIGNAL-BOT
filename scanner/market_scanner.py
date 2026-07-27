"""
BLISSFINITY AI SIGNAL BOT
MARKET SCANNER
"""

import ccxt
import pandas as pd

EXCHANGE = ccxt.mexc({
    "enableRateLimit": True,
})


# =====================================
# Load Top Volume USDT Pairs
# =====================================

def get_top_pairs(limit=100):

    markets = EXCHANGE.load_markets()

    tickers = EXCHANGE.fetch_tickers()

    pairs = []

    for symbol, market in markets.items():

        if not market.get("active", True):
            continue

        if market.get("spot", False):
            continue

        if "/USDT" not in symbol:
            continue

        ticker = tickers.get(symbol)

        if ticker is None:
            continue

        volume = ticker.get("quoteVolume", 0)

        if volume is None:
            volume = 0

        pairs.append((symbol, volume))

    pairs.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [

        pair

        for pair, _ in pairs[:limit]

    ]


# =====================================
# Download OHLCV
# =====================================

def get_dataframe(symbol, timeframe, limit=500):

    candles = EXCHANGE.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    return df


# =====================================
# Multi-Timeframe Data
# =====================================

def fetch_market_data(symbol):

    return {

        "1w": get_dataframe(symbol, "1w"),

        "1d": get_dataframe(symbol, "1d"),

        "4h": get_dataframe(symbol, "4h"),

        "15m": get_dataframe(symbol, "15m")

    }