"""
=====================================================
BLISSFINITY SIGNAL
Telegram Sender
Production Version
=====================================================
"""

from __future__ import annotations

import asyncio
import logging

import aiohttp

from config.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)

from telegram.formatter import (
    format_signal,
    format_entry,
    format_tp,
    format_stop,
    format_breakeven,
)


# =====================================================
# CONFIGURATION
# =====================================================

BASE_URL = (
    f"https://api.telegram.org/"
    f"bot{TELEGRAM_TOKEN}/sendMessage"
)

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

logger = logging.getLogger("Telegram")


# =====================================================
# TELEGRAM API
# =====================================================

async def send_message(text: str) -> bool:
    """
    Send a Telegram Markdown message.
    """

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:

        logger.warning(
            "Telegram credentials missing."
        )

        return False

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    for attempt in range(MAX_RETRIES):

        try:

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.post(
                    BASE_URL,
                    json=payload,
                ) as response:

                    if response.status == 200:

                        logger.info(
                            "Telegram message sent successfully."
                        )

                        return True

                    error_text = await response.text()

                    logger.error(
                        "Telegram Error (%s/%s): %s",
                        attempt + 1,
                        MAX_RETRIES,
                        error_text,
                    )

        except Exception:

            logger.exception(
                "Telegram request failed (%s/%s)",
                attempt + 1,
                MAX_RETRIES,
            )

        if attempt < MAX_RETRIES - 1:

            await asyncio.sleep(2)

    return False


# =====================================================
# NEW SIGNAL
# =====================================================

async def send_signal(
    signal: dict,
) -> bool:
    """
    Send a new trading signal.
    """

    return await send_message(
        format_signal(signal)
    )


# =====================================================
# ENTRY HIT
# =====================================================

async def send_entry_hit(
    trade: dict,
) -> bool:
    """
    Notify that trade entry has been reached.
    """

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    return await send_message(
        format_entry(
            symbol,
            direction,
        )
    )


# =====================================================
# TP1
# =====================================================

async def send_tp1_hit(
    trade: dict,
) -> bool:
    """
    Notify that TP1 has been reached.
    """

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    return await send_message(
        format_tp(
            symbol,
            direction,
            1,
            "2R",
        )
    )


# =====================================================
# TP2
# =====================================================

async def send_tp2_hit(
    trade: dict,
) -> bool:
    """
    Notify that TP2 has been reached.
    """

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    return await send_message(
        format_tp(
            symbol,
            direction,
            2,
            "3R",
        )
    )


# =====================================================
# STOP LOSS
# =====================================================

async def send_stop_loss(
    trade: dict,
) -> bool:
    """
    Notify that stop loss has been triggered.
    """

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    return await send_message(
        format_stop(
            symbol,
            direction,
        )
    )


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven(
    trade: dict,
) -> bool:
    """
    Notify that trade has closed at breakeven.
    """

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    return await send_message(
        format_breakeven(
            symbol,
            direction,
        )
    )


# =====================================================
# CUSTOM REPORT
# =====================================================

async def send_custom_report(
    title: str,
    report: dict,
) -> bool:
    """
    Send performance statistics.
    """

    total = report.get(
        "total",
        0,
    )

    wins = report.get(
        "wins",
        0,
    )

    losses = report.get(
        "losses",
        0,
    )

    breakevens = report.get(
        "breakevens",
        0,
    )

    win_rate = report.get(
        "win_rate",
        0,
    )

    total_rr = report.get(
        "total_rr",
        0,
    )

    average_rr = report.get(
        "average_rr",
        0,
    )

    message = (
        f"📊 *{title}*\n\n"
        f"Trades: *{total}*\n"
        f"Wins: *{wins}*\n"
        f"Losses: *{losses}*\n"
        f"Breakevens: *{breakevens}*\n\n"
        f"Win Rate: *{win_rate:.2f}%*\n"
        f"Net R: *{total_rr:.2f}R*\n"
        f"Average R: *{average_rr:.2f}R*"
    )

    return await send_message(
        message
    )


# =====================================================
# TEST CONNECTION
# =====================================================

async def send_test_message() -> bool:
    """
    Verify Telegram connectivity.
    """

    return await send_message(
        "✅ *BLISSFINITY SIGNAL*\n\n"
        "Telegram connection successful.\n\n"
        "Bot is online and ready."
    )


# =====================================================
# BOT STARTUP
# =====================================================

async def send_startup_message() -> bool:
    """
    Notify when the bot starts.
    """

    return await send_message(
        "🚀 *BLISSFINITY SIGNAL*\n\n"
        "Production Version\n\n"
        "Scanner Started\n"
        "Trade Tracker Started\n\n"
        "Monitoring markets..."
    )


# =====================================================
# BOT SHUTDOWN
# =====================================================

async def send_shutdown_message() -> bool:
    """
    Notify when the bot stops.
    """

    return await send_message(
        "🛑 *BLISSFINITY SIGNAL*\n\n"
        "Bot stopped.\n\n"
        "Monitoring paused."
    )


# =====================================================
# HEARTBEAT
# =====================================================

async def send_heartbeat() -> bool:
    """
    Optional system heartbeat.
    """

    return await send_message(
        "💚 *Bot Status*\n\n"
        "System Online\n\n"
        "Scanner Running\n"
        "Trade Tracker Running\n\n"
        "No issues detected."
    )

# =====================================================
# WEEKLY REPORT
# =====================================================

async def send_weekly_report(
    report: dict,
) -> bool:
    """
    Send weekly performance report.
    """

    return await send_custom_report(
        "Weekly Performance Report",
        report,
    )
