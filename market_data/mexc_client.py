import requests
import pandas as pd

BASE_URL = "https://contract.mexc.com"


INTERVAL_MAP = {
    "1m": "Min1",
    "5m": "Min5",
    "15m": "Min15",
    "30m": "Min30",
    "1h": "Min60",
    "4h": "Hour4",
    "1d": "Day1",
}


def get_klines(symbol="BTC_USDT", interval="15m", limit=200):
    """
    Download OHLCV candles from MEXC Futures API.
    Returns a pandas DataFrame.
    """

    interval = INTERVAL_MAP.get(interval, "Min15")

    url = (
        f"{BASE_URL}/api/v1/contract/kline/"
        f"{symbol}?interval={interval}&limit={limit}"
    )

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    if not data.get("success", False):
        raise Exception(data)

    d = data["data"]

    df = pd.DataFrame({
        "time": d["time"],
        "open": d["open"],
        "high": d["high"],
        "low": d["low"],
        "close": d["close"],
        "volume": d["vol"],
    })

    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float,
    })

    return df
