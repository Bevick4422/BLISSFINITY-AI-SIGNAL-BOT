"""
BLISSFINITY AI SIGNAL BOT
DATA MANAGER
"""

from scanner.market_scanner import fetch_market_data


def get_market_data(symbol):
    """
    Download all required timeframes once.
    """

    return {
        "15m": fetch_market_data(symbol, timeframe="15m"),
        "1h": fetch_market_data(symbol, timeframe="1h"),
        "4h": fetch_market_data(symbol, timeframe="4h"),
        "1d": fetch_market_data(symbol, timeframe="1d"),
        "1w": fetch_market_data(symbol, timeframe="1w"),
    }