"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Trade Tracker
=====================================================
"""

from __future__ import annotations

import asyncio
import logging

from database.repository import (
    get_active_trades,
    update_trade,
    close_trade,
)

from market_data.fetcher import (
    fetch_current_price,
)

from telegram.sender import (
    send_entry_message,
    send_tp_message,
    send_stop_message,
    send_breakeven_message,
)

# =====================================================
# CONFIGURATION
# =====================================================

CHECK_INTERVAL = 30  # Seconds

logger = logging.getLogger("TradeTracker")


# =====================================================
# DIRECTION HELPERS
# =====================================================

def is_buy(direction: str) -> bool:
    return direction.upper() == "BUY"


def is_sell(direction: str) -> bool:
    return direction.upper() == "SELL"


# =====================================================
# PRICE CHECKS
# =====================================================

def entry_hit(
    direction: str,
    current_price: float,
    entry: float,
) -> bool:

    if is_buy(direction):
        return current_price >= entry

    return current_price <= entry


def stop_hit(
    direction: str,
    current_price: float,
    stop_loss: float,
) -> bool:

    if is_buy(direction):
        return current_price <= stop_loss

    return current_price >= stop_loss


def target_hit(
    direction: str,
    current_price: float,
    target: float,
) -> bool:

    if is_buy(direction):
        return current_price >= target

    return current_price <= target


# =====================================================
# DATABASE HELPERS
# =====================================================

def mark_trade_open(trade: dict) -> bool:
    """
    Mark trade as OPEN.
    """

    return update_trade(
        trade["id"],
        state="OPEN",
        opened_at=None,
    )


def mark_tp1(trade: dict) -> bool:
    """
    Mark TP1 reached and activate break-even.
    """

    return update_trade(
        trade["id"],
        state="TP1_HIT",
        break_even=1,
        stop_loss=trade["entry"],
    )


def mark_closed(
    trade: dict,
    result: str,
    rr: float,
) -> bool:
    """
    Close trade.
    """

    return close_trade(
        trade["id"],
        result=result,
        rr=rr,
    )


# =====================================================
# DATA ACCESS
# =====================================================

def load_active_trades() -> list[dict]:
    """
    Load all active trades.
    """

    try:
        return get_active_trades()

    except Exception:
        logger.exception("Failed loading active trades")
        return []


def get_live_price(symbol: str) -> float | None:
    """
    Fetch latest market price.
    """

    try:
        return fetch_current_price(symbol)

    except Exception:
        logger.exception(f"Price fetch failed | {symbol}")
        return None
# =====================================================
# ENTRY MONITOR
# =====================================================

async def monitor_entry(trade: dict) -> bool:
    """
    Monitor pending trades and activate them once
    the market reaches the entry price.
    """

    if trade["state"] != "PENDING":
        return False

    current_price = get_live_price(trade["symbol"])

    if current_price is None:
        return False

    if not entry_hit(
        trade["direction"],
        current_price,
        trade["entry"],
    ):
        return False

    if not mark_trade_open(trade):
        return False

    trade["state"] = "OPEN"

    await send_entry_message(
        trade["symbol"],
        trade["direction"],
    )

    logger.info(
        "%s | Entry Triggered",
        trade["symbol"],
    )

    return True


# =====================================================
# TRADE MANAGEMENT
# =====================================================

async def monitor_trade(trade: dict) -> bool:
    """
    Manage active trades.
    """

    if trade["state"] not in ("OPEN", "TP1_HIT"):
        return False

    current_price = get_live_price(trade["symbol"])

    if current_price is None:
        return False

    direction = trade["direction"]

    # ==============================================
    # STOP LOSS / BREAKEVEN
    # ==============================================

    if stop_hit(
        direction,
        current_price,
        trade["stop_loss"],
    ):

        result = (
            "BREAKEVEN"
            if trade.get("break_even")
            else "LOSS"
        )

        rr = 0 if result == "BREAKEVEN" else -1

        mark_closed(
            trade,
            result=result,
            rr=rr,
        )

        if result == "BREAKEVEN":

            await send_breakeven_message(
                trade["symbol"],
                direction,
            )

        else:

            await send_stop_message(
                trade["symbol"],
                direction,
            )

        logger.info(
            "%s | %s",
            trade["symbol"],
            result,
        )

        return True

    # ==============================================
    # TAKE PROFIT 1
    # ==============================================

    if (
        trade["state"] == "OPEN"
        and target_hit(
            direction,
            current_price,
            trade["tp1"],
        )
    ):

        if not mark_tp1(trade):
            return False

        trade["state"] = "TP1_HIT"
        trade["break_even"] = 1
        trade["stop_loss"] = trade["entry"]

        await send_tp_message(
            trade["symbol"],
            direction,
            1,
            "1R",
        )

        logger.info(
            "%s | TP1 Hit",
            trade["symbol"],
        )

        return True

    # ==============================================
    # TAKE PROFIT 2
    # ==============================================

    if target_hit(
        direction,
        current_price,
        trade["tp2"],
    ):

        mark_closed(
            trade,
            result="WIN",
            rr=2,
        )

        await send_tp_message(
            trade["symbol"],
            direction,
            2,
            "2R",
        )

        logger.info(
            "%s | TP2 Hit",
            trade["symbol"],
        )

        return True

    return False
# =====================================================
# TRADE SCANNER
# =====================================================

async def check_active_trades() -> None:
    """
    Scan every active trade once.
    """

    trades = load_active_trades()

    if not trades:
        return

    logger.info(
        "Tracking %d active trade(s)...",
        len(trades),
    )

    for trade in trades:

        try:

            # -----------------------------------------
            # Pending Trades
            # -----------------------------------------

            if trade["state"] == "PENDING":

                activated = await monitor_entry(trade)

                if activated:
                    continue

            # -----------------------------------------
            # Active Trades
            # -----------------------------------------

            await monitor_trade(trade)

        except Exception:

            logger.exception(
                "Trade Tracker Error | %s",
                trade.get("symbol", "UNKNOWN"),
            )


# =====================================================
# MAIN LOOP
# =====================================================

async def run_trade_tracker() -> None:
    """
    Continuously monitor all active trades.
    """

    logger.info("Trade Tracker Started")

    while True:

        try:

            await check_active_trades()

        except Exception:

            logger.exception(
                "Unexpected tracker failure"
            )

        await asyncio.sleep(
            CHECK_INTERVAL
        )


# =====================================================
# MANUAL TEST
# =====================================================

async def _main() -> None:

    await run_trade_tracker()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    asyncio.run(_main())