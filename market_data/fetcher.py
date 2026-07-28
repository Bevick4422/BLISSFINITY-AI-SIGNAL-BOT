"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Market Data Fetcher
=====================================================
"""

from __future__ import annotations

import logging

import pandas as pd

from config.settings import (
    exchange,
    TREND_TIMEFRAME,
)

logger = logging.getLogger("MarketData")


# =====================================================
# DATAFRAME CONVERSION
# =====================================================

def _to_dataframe(ohlcv) -> pd.DataFrame | None:
    """
    Convert raw CCXT OHLCV data into a clean DataFrame.
    """

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
        unit="ms",
    )

    df.set_index("timestamp", inplace=True)

    for column in (
        "open",
        "high",
        "low",
        "close",
        "volume",
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df.dropna(inplace=True)

    return df


# =====================================================
# FETCH OHLCV
# =====================================================

def fetch_ohlcv(
    symbol: str,
    timeframe: str,
    limit: int = 300,
) -> pd.DataFrame | None:
    """
    Download OHLCV candles.
    """

    try:

        candles = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

        return _to_dataframe(candles)

    except Exception:

        logger.exception(
            "OHLCV fetch failed | %s | %s",
            symbol,
            timeframe,
        )

        return None


# =====================================================
# FETCH MARKET DATA
# =====================================================

def fetch_market_data(symbol: str) -> dict | None:
    """
    Load all market data required by the strategy.
    """

    daily = fetch_ohlcv(
        symbol,
        "1d",
        250,
    )

    trend = fetch_ohlcv(
        symbol,
        TREND_TIMEFRAME,
        300,
    )

    if daily is None or trend is None:
        return None

    if len(daily) < 50:
        return None

    if len(trend) < 100:
        return None

    return {
        "1d": daily,
        TREND_TIMEFRAME: trend,
    }


# =====================================================
# CURRENT PRICE
# =====================================================

def fetch_current_price(symbol: str) -> float | None:
    """
    Return latest traded price.
    """

    try:

        ticker = exchange.fetch_ticker(symbol)

        price = ticker.get("last")

        if price is None:
            return None

        return float(price)

    except Exception:

        logger.exception(
            "Price fetch failed | %s",
            symbol,
        )

        return None


# =====================================================
# HEALTH CHECK
# =====================================================

def exchange_health_check() -> bool:
    """
    Verify exchange connectivity.
    """

    try:

        exchange.fetch_time()

        return True

    except Exception:

        logger.exception(
            "Exchange health check failed."
        )

        return False


# =====================================================
# MANUAL TEST
# =====================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    pair = "BTC/USDT:USDT"

    logger.info("Testing market data...")

    market = fetch_market_data(pair)

    if market:

        logger.info(
            "Daily candles : %d",
            len(market["1d"]),
        )

        logger.info(
            "%s candles : %d",
            TREND_TIMEFRAME,
            len(market[TREND_TIMEFRAME]),
        )

    else:

        logger.error(
            "Market data unavailable."
        )

    price = fetch_current_price(pair)

    logger.info(
        "Current Price : %s",
        price,
    )

    logger.info(
        "Exchange Status : %s",
        "ONLINE" if exchange_health_check() else "OFFLINE",
    )