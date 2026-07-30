"""
=====================================================
BLISSFINITY
Trade Tracker
=====================================================
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from config.settings import TRACKER_INTERVAL

from database.repository import (
    get_active_trades,
    get_trade,
    open_trade,
    mark_tp1_hit,
    mark_tp2_hit,
    move_to_break_even,
    close_trade,
)

from market_data.fetcher import (
    fetch_current_price,
)

from telegram.sender import (
    send_entry_hit,
    send_tp1_hit,
    send_tp2_hit,
    send_stop_loss,
    send_breakeven,
)

logger = logging.getLogger("TradeTracker")


# =====================================================
# TIME
# =====================================================

def utc_now() -> datetime:
    """
    Return current UTC time.
    """
    return datetime.now(UTC)


def trade_duration_minutes(opened_at: str | None) -> int:
    """
    Calculate trade duration.
    """

    if not opened_at:
        return 0

    try:

        start = datetime.fromisoformat(opened_at)

        return int(
            (utc_now() - start).total_seconds() / 60
        )

    except Exception:

        return 0


# =====================================================
# TRADE TYPE
# =====================================================

def is_buy(trade: dict) -> bool:

    return trade["direction"].upper() == "BUY"


def is_sell(trade: dict) -> bool:

    return trade["direction"].upper() == "SELL"


# =====================================================
# PRICE CHECKS
# =====================================================

def entry_hit(
    trade: dict,
    price: float,
) -> bool:

    if is_buy(trade):

        return price <= trade["entry"]

    return price >= trade["entry"]


def tp1_hit(
    trade: dict,
    price: float,
) -> bool:

    if is_buy(trade):

        return price >= trade["tp1"]

    return price <= trade["tp1"]


def tp2_hit(
    trade: dict,
    price: float,
) -> bool:

    if is_buy(trade):

        return price >= trade["tp2"]

    return price <= trade["tp2"]


def stop_loss_hit(
    trade: dict,
    price: float,
) -> bool:

    if is_buy(trade):

        return price <= trade["stop_loss"]

    return price >= trade["stop_loss"]


def breakeven_hit(
    trade: dict,
    price: float,
) -> bool:

    if not trade["break_even"]:
        return False

    if is_buy(trade):

        return price <= trade["entry"]

    return price >= trade["entry"]


# =====================================================
# RISK / REWARD
# =====================================================

def calculate_rr(
    result: str,
) -> float:

    if result == "WIN":
        return 2.0

    if result == "LOSS":
        return -1.0

    return 0.0


# =====================================================
# ENTRY ACTIVATION
# =====================================================

async def activate_trade(
    trade: dict,
) -> None:
    """
    Activate trade when entry price is reached.
    """

    if not open_trade(trade["id"]):
        return

    logger.info(
        "%s | ENTRY HIT",
        trade["symbol"],
    )

    try:

        await send_entry_hit(trade)

    except Exception:

        logger.exception(
            "Failed to send entry notification."
        )
# =====================================================
# TP1 PROCESSING
# =====================================================

async def process_tp1(
    trade: dict,
) -> None:
    """
    Handle first take profit.
    """

    if not mark_tp1_hit(trade["id"]):
        return

    move_to_break_even(trade["id"])

    logger.info(
        "%s | TP1 HIT",
        trade["symbol"],
    )

    try:

        await send_tp1_hit(trade)

    except Exception:

        logger.exception(
            "Failed to send TP1 notification."
        )


# =====================================================
# TP2 PROCESSING
# =====================================================

async def process_tp2(
    trade: dict,
) -> None:
    """
    Handle final take profit.
    """

    duration = trade_duration_minutes(
        trade["opened_at"],
    )

    mark_tp2_hit(
        trade["id"],
    )

    close_trade(
        trade_id=trade["id"],
        result="WIN",
        rr=calculate_rr("WIN"),
        duration_minutes=duration,
    )

    logger.info(
        "%s | TP2 HIT",
        trade["symbol"],
    )

    try:

        await send_tp2_hit(trade)

    except Exception:

        logger.exception(
            "Failed to send TP2 notification."
        )


# =====================================================
# STOP LOSS PROCESSING
# =====================================================

async def process_stop_loss(
    trade: dict,
) -> None:
    """
    Handle stop loss.
    """

    duration = trade_duration_minutes(
        trade["opened_at"],
    )

    close_trade(
        trade_id=trade["id"],
        result="LOSS",
        rr=calculate_rr("LOSS"),
        duration_minutes=duration,
    )

    logger.info(
        "%s | STOP LOSS",
        trade["symbol"],
    )

    try:

        await send_stop_loss(trade)

    except Exception:

        logger.exception(
            "Failed to send stop loss notification."
        )


# =====================================================
# BREAKEVEN PROCESSING
# =====================================================

async def process_breakeven(
    trade: dict,
) -> None:
    """
    Close trade at break-even.
    """

    duration = trade_duration_minutes(
        trade["opened_at"],
    )

    close_trade(
        trade_id=trade["id"],
        result="BREAKEVEN",
        rr=calculate_rr("BREAKEVEN"),
        duration_minutes=duration,
    )

    logger.info(
        "%s | BREAKEVEN",
        trade["symbol"],
    )

    try:

        await send_breakeven(trade)

    except Exception:

        logger.exception(
            "Failed to send breakeven notification."
        )


# =====================================================
# PENDING TRADE
# =====================================================

async def monitor_pending_trade(
    trade: dict,
    price: float,
) -> None:
    """
    Waiting for entry.
    """

    if entry_hit(
        trade,
        price,
    ):

        await activate_trade(
            trade,
        )


# =====================================================
# OPEN TRADE
# =====================================================

async def monitor_open_trade(
    trade: dict,
    price: float,
) -> None:
    """
    Active trade.
    """

    if tp1_hit(
        trade,
        price,
    ):

        await process_tp1(
            trade,
        )

        return

    if stop_loss_hit(
        trade,
        price,
    ):

        await process_stop_loss(
            trade,
        )

        return


# =====================================================
# TP1 STATE
# =====================================================

async def monitor_tp1_trade(
    trade: dict,
    price: float,
) -> None:
    """
    Trade after TP1.
    """

    if tp2_hit(
        trade,
        price,
    ):

        await process_tp2(
            trade,
        )

        return

    if breakeven_hit(
        trade,
        price,
    ):

        await process_breakeven(
            trade,
        )

        return
# =====================================================
# SINGLE TRADE MONITOR
# =====================================================

async def monitor_trade(
    trade: dict,
) -> None:
    """
    Monitor one active trade.
    """

    try:

        latest = get_trade(
            trade["id"],
        )

        if latest is None:
            return

        # fetch_current_price() is synchronous
        price = fetch_current_price(
            latest["symbol"],
        )

        if price is None:
            return

        state = latest["state"]

        if state == "PENDING":

            await monitor_pending_trade(
                latest,
                price,
            )

            return

        if state == "OPEN":

            await monitor_open_trade(
                latest,
                price,
            )

            return

        if state == "TP1_HIT":

            await monitor_tp1_trade(
                latest,
                price,
            )

            return

    except asyncio.CancelledError:
        raise

    except Exception:

        logger.exception(
            "Error monitoring %s",
            trade["symbol"],
        )


# =====================================================
# MONITOR ALL TRADES
# =====================================================

async def monitor_all_trades() -> None:
    """
    Monitor every active trade.
    """

    trades = get_active_trades()

    if not trades:
        return

    await asyncio.gather(
        *[
            monitor_trade(trade)
            for trade in trades
        ],
        return_exceptions=True,
    )


# =====================================================
# TRACKER LOOP
# =====================================================

async def tracker_loop() -> None:
    """
    Main tracker loop.
    """

    print(">>> tracker_loop() entered <<<")

    logger.info("Trade Tracker Started")

    while True:

        try:

            await monitor_all_trades()

        except asyncio.CancelledError:
            raise

        except Exception:

            logger.exception(
                "Trade Tracker Loop Error"
            )

        await asyncio.sleep(
            TRACKER_INTERVAL,
        )


# =====================================================
# ENTRY POINT
# =====================================================

async def run_trade_tracker() -> None:

    print(">>> run_trade_tracker() started <<<")

    logger.info("Trade Tracker Started")

    await tracker_loop()

# =====================================================
# MANUAL TEST
# =====================================================

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    asyncio.run(
        run_trade_tracker()
    )