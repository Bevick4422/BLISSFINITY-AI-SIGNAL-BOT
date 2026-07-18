
"""
BLISSFINITY AI SIGNAL BOT
MULTI-TIMEFRAME MARKET SCANNER
"""

import ccxt
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

EXCHANGE = ccxt.mexc({
    "enableRateLimit": True
})


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


def fetch_market_data(symbol):

    return {

        "1w": get_dataframe(symbol, "1w"),

        "1d": get_dataframe(symbol, "1d"),

        "4h": get_dataframe(symbol, "4h"),

        "15m": get_dataframe(symbol, "15m")

    }