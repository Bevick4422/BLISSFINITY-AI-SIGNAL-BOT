"""
BLISSFINITY AI SIGNAL BOT
MARKET DATA FETCHER
"""

import pandas as pd

from config.settings import exchange


# ==========================================================
# Convert OHLCV to DataFrame
# ==========================================================

def _to_dataframe(ohlcv):

    if not ohlcv:
        return None

    df = pd.DataFrame(
        ohlcv,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    df.set_index("timestamp", inplace=True)

    for column in [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df.dropna(inplace=True)

    return df


# ==========================================================
# Fetch One Timeframe
# ==========================================================

def fetch_ohlcv(
    symbol,
    timeframe,
    limit=300,
):

    try:

        data = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

        return _to_dataframe(data)

    except Exception as e:

        print(
            f"{symbol} | {timeframe} | {e}"
        )

        return None


# ==========================================================
# Fetch Complete Market Data
# ==========================================================

def fetch_market_data(symbol):

    daily = fetch_ohlcv(
        symbol,
        "1d",
        limit=250,
    )

    h4 = fetch_ohlcv(
        symbol,
        "4h",
        limit=300,
    )

    if daily is None:

        return None

    if h4 is None:

        return None

    if len(daily) < 50:

        return None

    if len(h4) < 100:

        return None

    return {

        "1d": daily,

        "4h": h4,

    }


# ==========================================================
# Manual Test
# ==========================================================

if __name__ == "__main__":

    market = fetch_market_data(
        "BTC/USDT:USDT"
    )

    if market:

        print("Daily Candles :", len(market["1d"]))
        print("H4 Candles    :", len(market["4h"]))

    else:

        print("Market data unavailable.")