"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Trade Tracker
Production Version
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

logger = logging.getLogger(__name__)


# =====================================================
# TIME
# =====================================================

def utc_now() -> datetime:
    """
    Current UTC datetime.
    """

    return datetime.now(UTC)


# =====================================================
# DURATION
# =====================================================

def trade_duration_minutes(
    opened_at: str,
) -> int:
    """
    Calculate trade duration.
    """

    if not opened_at:
        return 0

    start = datetime.fromisoformat(opened_at)

    return int(
        (
            utc_now() - start
        ).total_seconds() / 60
    )


# =====================================================
# PRICE HELPERS
# =====================================================

def is_buy(
    trade: dict,
) -> bool:

    return trade["direction"].upper() == "BUY"


def is_sell(
    trade: dict,
) -> bool:

    return trade["direction"].upper() == "SELL"


# =====================================================
# ENTRY CHECK
# =====================================================

def entry_hit(
    trade: dict,
    price: float,
) -> bool:

    entry = trade["entry"]

    if is_buy(trade):

        return price <= entry

    return price >= entry


# =====================================================
# TP1 CHECK
# =====================================================

def tp1_hit(
    trade: dict,
    price: float,
) -> bool:

    tp1 = trade["tp1"]

    if is_buy(trade):

        return price >= tp1

    return price <= tp1


# =====================================================
# TP2 CHECK
# =====================================================

def tp2_hit(
    trade: dict,
    price: float,
) -> bool:

    tp2 = trade["tp2"]

    if is_buy(trade):

        return price >= tp2

    return price <= tp2


# =====================================================
# STOP LOSS CHECK
# =====================================================

def stop_loss_hit(
    trade: dict,
    price: float,
) -> bool:

    sl = trade["stop_loss"]

    if is_buy(trade):

        return price <= sl

    return price >= sl


# =====================================================
# BREAKEVEN CHECK
# =====================================================

def breakeven_hit(
    trade: dict,
    price: float,
) -> bool:

    if not trade["break_even"]:
        return False

    entry = trade["entry"]

    if is_buy(trade):

        return price <= entry

    return price >= entry


# =====================================================
# RR CALCULATION
# =====================================================

def calculate_rr(
    trade: dict,
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
    Mark trade as OPEN and notify Telegram.
    """

    trade_id = trade["id"]

    success = open_trade(trade_id)

    if not success:
        return

    logger.info(
        "%s ENTRY HIT",
        trade["symbol"],
    )

    try:
        await send_entry_hit(trade)
    except Exception:
        logger.exception(
            "Failed sending ENTRY notification."
        )


# =====================================================
# TP1 PROCESSING
# =====================================================

async def process_tp1(
    trade: dict,
) -> None:
    """
    Handle TP1 event.
    """

    trade_id = trade["id"]

    success = mark_tp1_hit(trade_id)

    if not success:
        return

    move_to_break_even(trade_id)

    logger.info(
        "%s TP1 HIT",
        trade["symbol"],
    )

    try:
        await send_tp1_hit(trade)
    except Exception:
        logger.exception(
            "Failed sending TP1 notification."
        )


# =====================================================
# SINGLE TRADE CHECK
# =====================================================

async def monitor_trade(
    trade: dict,
) -> None:
    """
    Monitor one active trade.
    """

    try:

        latest = get_trade(trade["id"])

        if latest is None:
            return

        symbol = latest["symbol"]

        price = await fetch_current_price(symbol)

        if price is None:
            return

        state = latest["state"]

        # --------------------------------------------
        # Waiting For Entry
        # --------------------------------------------

        if state == "PENDING":

            if entry_hit(
                latest,
                price,
            ):
                await activate_trade(latest)

            return

        # --------------------------------------------
        # OPEN
        # --------------------------------------------

        if state == "OPEN":

            if tp1_hit(
                latest,
                price,
            ):
                await process_tp1(latest)
                return

            if stop_loss_hit(
                latest,
                price,
            ):
                duration = trade_duration_minutes(
                    latest["opened_at"],
                )

                close_trade(
                    latest["id"],
                    result="LOSS",
                    rr=calculate_rr(
                        latest,
                        "LOSS",
                    ),
                    duration_minutes=duration,
                )

                logger.info(
                    "%s STOP LOSS",
                    symbol,
                )

                try:
                    await send_stop_loss(latest)
                except Exception:
                    logger.exception(
                        "Failed sending SL notification."
                    )

                return

        # --------------------------------------------
        # TP1 HIT
        # --------------------------------------------

        if state == "TP1_HIT":

            if tp2_hit(
                latest,
                price,
            ):
                return

            if breakeven_hit(
                latest,
                price,
            ):
                return

    except Exception:

        logger.exception(
            "Trade tracker error."
        )


# =====================================================
# MONITOR ALL TRADES
# =====================================================

async def monitor_all_trades() -> None:
    """
    Check every active trade.
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
# TP2 PROCESSING
# =====================================================

async def process_tp2(
    trade: dict,
) -> None:
    """
    Final target reached.
    Close remaining position.
    """

    trade_id = trade["id"]

    success = mark_tp2_hit(trade_id)

    if not success:
        return

    duration = trade_duration_minutes(
        trade["opened_at"],
    )

    close_trade(
        trade_id,
        result="WIN",
        rr=calculate_rr(
            trade,
            "WIN",
        ),
        duration_minutes=duration,
    )

    logger.info(
        "%s TP2 HIT",
        trade["symbol"],
    )

    try:
        await send_tp2_hit(trade)

    except Exception:

        logger.exception(
            "Failed sending TP2 notification."
        )


# =====================================================
# BREAKEVEN PROCESSING
# =====================================================

async def process_breakeven(
    trade: dict,
) -> None:
    """
    Price returned to entry
    after TP1.
    """

    duration = trade_duration_minutes(
        trade["opened_at"],
    )

    close_trade(
        trade["id"],
        result="BREAKEVEN",
        rr=calculate_rr(
            trade,
            "BREAKEVEN",
        ),
        duration_minutes=duration,
    )

    logger.info(
        "%s BREAKEVEN",
        trade["symbol"],
    )

    try:

        await send_breakeven(trade)

    except Exception:

        logger.exception(
            "Failed sending breakeven notification."
        )


# =====================================================
# TP1 STATE MONITOR
# =====================================================

async def monitor_tp1_trade(
    trade: dict,
    price: float,
) -> None:
    """
    Monitor trades that
    already reached TP1.
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
# OPEN STATE MONITOR
# =====================================================

async def monitor_open_trade(
    trade: dict,
    price: float,
) -> None:
    """
    Monitor active trades.
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

        duration = trade_duration_minutes(
            trade["opened_at"],
        )

        close_trade(
            trade["id"],
            result="LOSS",
            rr=calculate_rr(
                trade,
                "LOSS",
            ),
            duration_minutes=duration,
        )

        logger.info(
            "%s STOP LOSS",
            trade["symbol"],
        )

        try:

            await send_stop_loss(
                trade,
            )

        except Exception:

            logger.exception(
                "Failed sending stop loss notification."
            )

        return


# =====================================================
# ENTRY STATE MONITOR
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
# TRADE DISPATCHER
# =====================================================

async def monitor_trade(
    trade: dict,
) -> None:
    """
    Monitor a single trade.
    """

    try:

        latest = get_trade(
            trade["id"],
        )

        if latest is None:
            return

        price = await fetch_current_price(
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
# MONITOR ALL ACTIVE TRADES
# =====================================================

async def monitor_all_trades() -> None:
    """
    Monitor every active trade concurrently.
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
    Main tracking loop.
    """

    logger.info(
        "Trade Tracker Started"
    )

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
            TRACKER_INTERVAL
        )


# =====================================================
# ENTRY POINT
# =====================================================

async def run_trade_tracker() -> None:
    """
    Entry point used by main.py
    """

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