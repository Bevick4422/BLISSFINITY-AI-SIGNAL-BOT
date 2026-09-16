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
from datetime import UTC, datetime

from config.settings import (
    SYMBOLS,
    SCAN_INTERVAL,
    MAX_DAILY_SIGNALS,
)

from database.models import create_tables

from market_data.fetcher import (
    fetch_market_data,
    fetch_current_price,
)

from engine.strategy_engine import evaluate_symbol

from telegram.sender import (
    send_signal,
    send_entry_hit,
    send_tp1_hit,
    send_tp2_hit,
    send_stop_loss,
    send_breakeven,
)

from tracking.trade_tracker import (
    record_signal,
    get_active_trades,
    update_trade,
    get_performance,
)

from utils.trade_validator import validate_trade


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("BLISSFINITY")


# =====================================================
# DAILY SIGNAL CONTROL
# =====================================================

signals_today = 0
current_day = datetime.now(UTC).date()


def reset_daily_counter() -> None:
    """
    Reset the daily signal counter when a new UTC day begins.
    """

    global current_day
    global signals_today

    today = datetime.now(UTC).date()

    if today != current_day:
        current_day = today
        signals_today = 0

        logger.info("Daily signal counter reset.")


def daily_limit_reached() -> bool:
    """
    Return True when the daily signal limit has been reached.
    """

    return signals_today >= MAX_DAILY_SIGNALS


# =====================================================
# STARTUP
# =====================================================

def startup() -> None:
    """
    Initialize the application.
    """

    print("\n" + "=" * 60)
    print("BLISSFINITY SIGNALS")
    print("Production Version")
    print("=" * 60 + "\n")

    create_tables()

    logger.info("Database Ready")
    logger.info("Symbols Loaded : %s", len(SYMBOLS))
    logger.info("Daily Limit    : %s", MAX_DAILY_SIGNALS)
    logger.info("Scan Interval  : %s seconds", SCAN_INTERVAL)


# =====================================================
# SIGNAL SCANNING
# =====================================================

async def scan_symbol(symbol: str) -> None:
    """
    Scan one symbol and record a valid trading signal.
    """

    global signals_today

    try:
        logger.info("Scanning %s", symbol)

        market_data = fetch_market_data(symbol)

        if market_data is None:
            logger.warning(
                "No market data returned for %s",
                symbol,
            )
            return

        signal = evaluate_symbol(
            symbol=symbol,
            market_data=market_data,
        )

        if signal is None:
            logger.info(
                "No valid setup found for %s",
                symbol,
            )
            return

        if not validate_trade(signal):
            logger.warning(
                "Invalid signal rejected for %s",
                symbol,
            )
            return

        trade_id = record_signal(signal)

        if trade_id is None:
            logger.warning(
                "Failed to record trade for %s",
                symbol,
            )
            return

        signal["trade_id"] = trade_id

        telegram_sent = await send_signal(signal)

        if not telegram_sent:
            logger.warning(
                "Signal recorded but Telegram notification failed | %s",
                trade_id,
            )

        signals_today += 1

        logger.info(
            "SIGNAL RECORDED | ID: %s | %s | %s",
            trade_id,
            signal["direction"],
            symbol,
        )

        logger.info(
            "Signals Today: %s/%s",
            signals_today,
            MAX_DAILY_SIGNALS,
        )

    except Exception:
        logger.exception(
            "Scan failed for %s",
            symbol,
        )


async def scan_market() -> None:
    """
    Scan all configured symbols until the daily limit is reached.
    """

    reset_daily_counter()

    if daily_limit_reached():
        logger.info(
            "Daily signal limit reached: %s/%s",
            signals_today,
            MAX_DAILY_SIGNALS,
        )
        return

    for symbol in SYMBOLS:
        if daily_limit_reached():
            logger.info(
                "Daily signal limit reached. Stopping scan."
            )
            break

        await scan_symbol(symbol)


# =====================================================
# ACTIVE TRADE MONITORING
# =====================================================

async def monitor_active_trades() -> None:
    """
    Monitor pending and open trades.

    Notifications are sent only when a new trade event is detected:
    - Entry reached
    - TP1 reached
    - TP2 reached
    - Stop-loss reached
    - Final breakeven closure
    """

    active_trades = get_active_trades()

    if not active_trades:
        return

    logger.info(
        "Monitoring %s active trade(s)",
        len(active_trades),
    )

    for trade in active_trades:
        symbol = trade.get("symbol", "UNKNOWN")
        trade_id = trade.get("trade_id")

        try:
            current_price = fetch_current_price(symbol)

            if current_price is None:
                logger.warning(
                    "Current price unavailable | %s | Trade: %s",
                    symbol,
                    trade_id,
                )
                continue

            previous_status = trade.get("status")
            previous_state = trade.get("state")
            previous_tp1_hit = bool(trade.get("tp1_hit", False))
            previous_stop_loss = trade.get("stop_loss")

            updated_trade = update_trade(
                trade_id=trade_id,
                current_price=current_price,
            )

            if updated_trade is None:
                logger.warning(
                    "Trade update returned no result | %s",
                    trade_id,
                )
                continue

            new_status = updated_trade.get("status")
            new_state = updated_trade.get("state")
            new_tp1_hit = bool(updated_trade.get("tp1_hit", False))
            new_stop_loss = updated_trade.get("stop_loss")

            # -------------------------------------------------
            # ENTRY REACHED
            # -------------------------------------------------

            if (
                previous_status == "PENDING"
                and new_status == "OPEN"
            ):
                sent = await send_entry_hit(updated_trade)

                logger.info(
                    "ENTRY HIT | %s | Price: %s | Telegram: %s",
                    symbol,
                    current_price,
                    sent,
                )

            # -------------------------------------------------
            # TP1 REACHED
            # -------------------------------------------------

            if (
                not previous_tp1_hit
                and new_tp1_hit
            ):
                sent = await send_tp1_hit(updated_trade)

                logger.info(
                    "TP1 HIT | %s | Price: %s | Telegram: %s",
                    symbol,
                    current_price,
                    sent,
                )

                logger.info(
                    "STOP MOVED TO BREAKEVEN | %s | Entry: %s",
                    symbol,
                    updated_trade.get("entry"),
                )

            # -------------------------------------------------
            # FINAL WIN
            # -------------------------------------------------

            terminal_statuses = {
                "WIN",
                "LOSS",
                "BREAKEVEN",
            }

            if (
                new_status in terminal_statuses
                and previous_status not in terminal_statuses
            ):
                if new_status == "WIN":
                    sent = await send_tp2_hit(updated_trade)

                    logger.info(
                        "TP2 HIT | %s | Price: %s | Telegram: %s",
                        symbol,
                        current_price,
                        sent,
                    )

                elif new_status == "LOSS":
                    sent = await send_stop_loss(updated_trade)

                    logger.info(
                        "STOP LOSS HIT | %s | Price: %s | Telegram: %s",
                        symbol,
                        current_price,
                        sent,
                    )

                elif new_status == "BREAKEVEN":
                    sent = await send_breakeven(updated_trade)

                    logger.info(
                        "BREAKEVEN CLOSED | %s | Price: %s | Telegram: %s",
                        symbol,
                        current_price,
                        sent,
                    )

                logger.info(
                    "TRADE CLOSED | ID: %s | Symbol: %s | "
                    "Result: %s | R: %s",
                    trade_id,
                    symbol,
                    new_status,
                    updated_trade.get("r_multiple"),
                )

            # -------------------------------------------------
            # GENERAL TRADE UPDATE
            # -------------------------------------------------

            if (
                new_status != previous_status
                or new_state != previous_state
                or new_stop_loss != previous_stop_loss
            ):
                logger.info(
                    "TRADE UPDATE | ID: %s | %s | "
                    "Status: %s -> %s | "
                    "State: %s -> %s | "
                    "Stop Loss: %s -> %s | "
                    "Price: %s",
                    trade_id,
                    symbol,
                    previous_status,
                    new_status,
                    previous_state,
                    new_state,
                    previous_stop_loss,
                    new_stop_loss,
                    current_price,
                )

        except Exception:
            logger.exception(
                "Trade monitoring failed | %s | Trade: %s",
                symbol,
                trade_id,
            )


# =====================================================
# PERFORMANCE LOGGING
# =====================================================

def log_performance() -> None:
    """
    Log current trade performance.
    """

    performance = get_performance()

    logger.info(
        "PERFORMANCE | "
        "Total: %s | "
        "Pending: %s | "
        "Open: %s | "
        "Wins: %s | "
        "Losses: %s | "
        "Breakevens: %s | "
        "Active: %s | "
        "Net R: %s | "
        "Win Rate: %.2f%%",
        performance["total_trades"],
        performance["pending_trades"],
        performance["open_trades"],
        performance["wins"],
        performance["losses"],
        performance["breakevens"],
        performance["active_trades"],
        performance["net_r"],
        performance["win_rate"],
    )


# =====================================================
# MAIN SCANNER LOOP
# =====================================================

async def run_scanner() -> None:
    """
    Run trade monitoring and market scanning continuously.
    """

    logger.info("Scanner Started")

    while True:
        try:
            # Monitor existing trades first.
            await monitor_active_trades()

            # Scan for new trading opportunities.
            await scan_market()

            # Display current performance.
            log_performance()

        except Exception:
            logger.exception("Scanner loop error")

        await asyncio.sleep(SCAN_INTERVAL)


# =====================================================
# APPLICATION ENTRY POINT
# =====================================================

async def main() -> None:
    """
    Application entry point.
    """

    startup()
    await run_scanner()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("BLISSFINITY SIGNAL stopped by user.")

    except Exception:
        logger.exception("Fatal application error.")
        traceback.print_exc()