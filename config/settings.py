
"""
=========================================================
BLISSFINITY AI SIGNAL BOT
Configuration
=========================================================
"""

from __future__ import annotations

import logging
import os

import ccxt

from config.crypto_universe import CRYPTO_UNIVERSE

# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger("Config")

# ==========================================================
# TELEGRAM
# ==========================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# ==========================================================
# BOT SETTINGS
# ==========================================================

SCAN_INTERVAL = 60               # Seconds
MIN_DAILY_SIGNALS = 3
MAX_DAILY_SIGNALS = 4
MAX_PAIRS = 100

# ==========================================================
# TIMEFRAMES
# ==========================================================

TREND_TIMEFRAME = "4h"
BOS_TIMEFRAME = "4h"
ENTRY_TIMEFRAME = "15m"

# ==========================================================
# RISK SETTINGS
# ==========================================================

DEFAULT_RISK_REWARD = 2
MAX_STALE_ENTRY_PERCENT = 2.0

# ==========================================================
# MEXC EXCHANGE
# ==========================================================

exchange = ccxt.mexc(
    {
        "enableRateLimit": True,
        "timeout": 30000,
        "options": {
            "defaultType": "swap",
        },
    }
)

# ==========================================================
# LOAD SYMBOLS
# ==========================================================

def get_symbols() -> list[str]:
    """
    Load approved USDT perpetual futures.
    """

    logger.info("Loading MEXC perpetual futures...")

    try:

        exchange.load_markets()

        symbols = []

        for symbol, market in exchange.markets.items():

            if not market.get("active"):
                continue

            if not market.get("swap"):
                continue

            if not market.get("linear"):
                continue

            if market.get("quote") != "USDT":
                continue

            base = str(
                market.get("base", "")
            ).upper()

            if base not in CRYPTO_UNIVERSE:
                continue

            symbols.append(symbol)

        symbols = sorted(set(symbols))

        logger.info(
            "Loaded %d trading pairs.",
            len(symbols),
        )

        return symbols[:MAX_PAIRS]

    except Exception:

        logger.exception(
            "Unable to load markets."
        )

        return []


# ==========================================================
# SYMBOL LIST
# ==========================================================

SYMBOLS = get_symbols()


# ==========================================================
# STARTUP INFO
# ==========================================================

logger.info("=" * 60)
logger.info("BLISSFINITY AI SIGNAL BOT")
logger.info("=" * 60)
logger.info("Trading Pairs : %d", len(SYMBOLS))
logger.info("Scan Interval : %s seconds", SCAN_INTERVAL)
logger.info(
    "Daily Signals : %d - %d",
    MIN_DAILY_SIGNALS,
    MAX_DAILY_SIGNALS,
)
logger.info("=" * 60)

# =====================================================
# TRADE TRACKER
# =====================================================

TRACKER_INTERVAL = 15  # seconds