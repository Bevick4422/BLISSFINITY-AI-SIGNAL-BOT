
"""
=====================================================
BLISSFINITY SIGNAL
Production Main
=====================================================
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from datetime import datetime, UTC

from config.settings import (
    SYMBOLS,
    SCAN_INTERVAL,
    MAX_DAILY_SIGNALS,
)

from database.models import create_tables

from tracking.trade_manager import (
    add_trade,
)

from tracking.trade_tracker import (
    run_trade_tracker,
)

from market_data.fetcher import (
    fetch_market_data,
)

from engine.strategy_engine import (
    evaluate_symbol,
)

from telegram.sender import (
    send_signal,
)

from utils.trade_validator import (
    validate_trade,
)

from utils.anti_spam import (
    is_duplicate_signal,
)
from reports.report_scheduler import (
    run_report_scheduler,
)

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
current_day = datetime.now(UTC).date()

# =====================================================
# DAILY RESET
# =====================================================

def reset_daily_counter():

    global current_day
    global signals_today

    today = datetime.now(UTC).date()

    if today != current_day:

        current_day = today
        signals_today = 0

        logger.info("Daily signal counter reset.")

# =====================================================
# DAILY LIMIT
# =====================================================

def daily_limit_reached():

    return signals_today >= MAX_DAILY_SIGNALS


# =====================================================
# STARTUP
# =====================================================

def startup():

    print("\n" + "=" * 60)
    print("BLISSFINITY SIGNALS")
    print("Production Version")
    print("=" * 60 + "\n")

    create_tables()

    logger.info("Database Ready")
    logger.info("Symbols Loaded : %s", len(SYMBOLS))
    logger.info("Daily Limit    : %s", MAX_DAILY_SIGNALS)
    logger.info("Scan Interval  : %s sec", SCAN_INTERVAL)


# =====================================================
# SCAN SYMBOL
# =====================================================

async def scan_symbol(symbol):

    global signals_today

    try:

        logger.info("Scanning %s", symbol)

        # ---------------------------------
        # Fetch Market Data
        # ---------------------------------

        market = fetch_market_data(symbol)

        if market is None:
            return

        # ---------------------------------
        # Generate Signal
        # ---------------------------------

        signal = evaluate_symbol(
            symbol=symbol,
            market=market,
        )

        if signal is None:
            return

        # ---------------------------------
        # Validate Trade
        # ---------------------------------

        if not validate_trade(signal):

            logger.warning(
                "Invalid signal rejected for %s",
                symbol,
            )

            return

        # ---------------------------------
        # Prevent Duplicate Signals
        # ---------------------------------

        if is_duplicate_signal(signal):

            logger.info(
                "Duplicate signal skipped for %s",
                symbol,
            )

            return

        # ---------------------------------
        # Save Trade
        # ---------------------------------

        trade_id = add_trade(signal)

        if trade_id is None:

            logger.warning(
                "Failed to save trade for %s",
                symbol,
            )

            return

        signal["trade_id"] = trade_id

        # ---------------------------------
        # Send Telegram Signal
        # ---------------------------------

        await send_signal(signal)

        signals_today += 1

        logger.info(
            "Signals Today %s/%s",
            signals_today,
            MAX_DAILY_SIGNALS,
        )

    except Exception:

        logger.exception(
            "%s Scan Failed",
            symbol,
        )
# =====================================================
# SCAN MARKET
# =====================================================

async def scan_market():

    reset_daily_counter()

    if daily_limit_reached():

        logger.info("Daily limit reached.")

        return

    for symbol in SYMBOLS:

        if daily_limit_reached():
            break

        await scan_symbol(symbol)


# =====================================================
# SCANNER LOOP
# =====================================================

async def run_scanner():

    logger.info("Scanner Started")

    while True:

        try:

            await scan_market()

        except Exception:

            logger.exception(
                "Scanner Loop Error"
            )

        await asyncio.sleep(
            SCAN_INTERVAL
        )


# =====================================================
# MAIN
# =====================================================

async def main():

    startup()

    await asyncio.gather(
        run_scanner(),
        run_trade_tracker(),
        run_report_scheduler(),
    )
# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        logger.info(
            "Bot stopped."
        )

    except Exception:

        traceback.print_exc()