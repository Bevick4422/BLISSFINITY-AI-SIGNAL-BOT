
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Main v10
=====================================================
"""

from __future__ import annotations

import asyncio
import logging
import traceback

from datetime import datetime
from typing import Optional

# =====================================================
# CONFIG
# =====================================================

from config.settings import (
    SYMBOLS,
    SCAN_INTERVAL,
    MAX_DAILY_SIGNALS,
)

# =====================================================
# DATABASE
# =====================================================

from database.models import create_tables
from tracking.trade_manager import save_trade

# =====================================================
# MARKET
# =====================================================

from market_data.fetcher import fetch_market_data

# =====================================================
# STRATEGY
# =====================================================

from engine.strategy_engine import evaluate_symbol

# =====================================================
# TELEGRAM
# =====================================================

from telegram.sender import send_signal

# =====================================================
# LOGGER
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("BLISSFINITY")

# =====================================================
# GLOBALS
# =====================================================

signals_today = 0

current_day = datetime.utcnow().date()

running = True

# =====================================================
# DAILY RESET
# =====================================================

def reset_daily_counter():

    global current_day
    global signals_today

    today = datetime.utcnow().date()

    if today != current_day:

        current_day = today

        signals_today = 0

        logger.info(
            "Daily signal counter reset."
        )

# =====================================================
# DAILY LIMIT
# =====================================================

def daily_limit_reached():

    return signals_today >= MAX_DAILY_SIGNALS

# =====================================================
# STARTUP
# =====================================================

def startup():

    print()

    print("=" * 60)

    print("BLISSFINITY AI SIGNAL BOT")

    print("Production Version")

    print("=" * 60)

    print()

    logger.info("Initializing database...")

    create_tables()

    logger.info("Database ready.")

    logger.info(
        "Loaded %s trading pairs.",
        len(SYMBOLS),
    )

    logger.info(
        "Daily Signal Limit : %s",
        MAX_DAILY_SIGNALS,
    )

    logger.info(
        "Scan Interval : %s seconds",
        SCAN_INTERVAL,
    )

    print()

# =====================================================
# SCAN ONE SYMBOL
# =====================================================

async def scan_symbol(
    symbol: str,
) -> Optional[dict]:

    global signals_today

    try:

        logger.info(
            "Scanning %s",
            symbol,
        )

        market = fetch_market_data(symbol)

        if market is None:

            logger.warning(
                "%s | Market unavailable",
                symbol,
            )

            return None

        signal = evaluate_symbol(
            symbol=symbol,
            market=market,
        )

        if signal is None:

            return None
        # =============================================
        # SAVE TRADE
        # =============================================

        trade_id = save_trade(signal)

        if trade_id is None:

            logger.info(
                "%s | Trade rejected.",
                symbol,
            )

            return None

        signal["trade_id"] = trade_id

        # =============================================
        # TELEGRAM
        # =============================================

        sent = await send_signal(signal)

        if sent:

            logger.info(
                "%s | Telegram sent.",
                symbol,
            )

        else:

            logger.warning(
                "%s | Telegram failed.",
                symbol,
            )

        # =============================================
        # DAILY COUNT
        # =============================================

        signals_today += 1

        logger.info(

            "Signals Today : %s/%s",

            signals_today,

            MAX_DAILY_SIGNALS,

        )

        return signal

    except Exception as e:

        logger.error(

            "%s | Scan Failed",

            symbol,

        )

        traceback.print_exc()

        return None


# =====================================================
# SCAN MARKET
# =====================================================

async def scan_market():

    reset_daily_counter()

    if daily_limit_reached():

        logger.info(

            "Daily signal limit reached."

        )

        return

    logger.info(

        "Scanning %s symbols...",

        len(SYMBOLS),

    )

    for symbol in SYMBOLS:

        if daily_limit_reached():

            logger.info(

                "Maximum daily signals reached."

            )

            break

        await scan_symbol(symbol)


# =====================================================
# MAIN LOOP
# =====================================================

async def run():

    startup()

    logger.info(

        "Scanner Started."

    )

    while running:

        try:

            await scan_market()

        except Exception:

            logger.exception(

                "Scanner Loop Error"

            )

        logger.info(

            "Sleeping %s seconds...",

            SCAN_INTERVAL,

        )

        await asyncio.sleep(

            SCAN_INTERVAL

        )
# =====================================================
# SHUTDOWN
# =====================================================

async def shutdown():

    logger.info("")

    logger.info("=" * 60)

    logger.info(
        "BLISSFINITY AI SIGNAL BOT STOPPED"
    )

    logger.info("=" * 60)

    logger.info("Shutdown Complete.")


# =====================================================
# ENTRY POINT
# =====================================================

async def main():

    try:

        await run()

    except asyncio.CancelledError:

        logger.info(
            "Task Cancelled."
        )

    except KeyboardInterrupt:

        logger.info(
            "Keyboard Interrupt."
        )

    except Exception:

        logger.exception(
            "Fatal Error"
        )

    finally:

        await shutdown()


# =====================================================
# START BOT
# =====================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()

        print("=" * 60)

        print("Bot stopped by user.")

        print("=" * 60)

    except Exception:

        traceback.print_exc()