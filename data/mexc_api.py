import ccxt
import pandas as pd

exchange = ccxt.mexc()


def fetch_ohlcv(symbol, timeframe, limit=500):
    candles = exchange.fetch_ohlcv(
        symbol=symbol,
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

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    return df
