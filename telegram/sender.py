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
from typing import Any

import aiohttp

from config.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_COMMUNITY_CHAT_ID,
    TELEGRAM_TOKEN,
)

from telegram.formatter import (
    format_breakeven,
    format_entry,
    format_signal,
    format_stop,
    format_tp,
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
RETRY_DELAY = 2

logger = logging.getLogger("Telegram")


# =====================================================
# DESTINATIONS
# =====================================================

def get_chat_ids() -> list[str]:
    """
    Return all configured Telegram destinations.

    Duplicate or empty chat IDs are removed.
    """

    chat_ids = [
        TELEGRAM_CHAT_ID,
        TELEGRAM_COMMUNITY_CHAT_ID,
    ]

    unique_chat_ids: list[str] = []

    for chat_id in chat_ids:
        if not chat_id:
            continue

        normalized_chat_id = str(chat_id).strip()

        if not normalized_chat_id:
            continue

        if normalized_chat_id not in unique_chat_ids:
            unique_chat_ids.append(normalized_chat_id)

    return unique_chat_ids


# =====================================================
# TELEGRAM API
# =====================================================

async def send_message(text: str) -> bool:
    """
    Send one message to every configured Telegram destination.

    Returns True only when the message is successfully sent
    to all configured destinations.
    """

    if not TELEGRAM_TOKEN:
        logger.warning("Telegram token is missing.")
        return False

    if not text or not text.strip():
        logger.warning("Telegram message is empty.")
        return False

    chat_ids = get_chat_ids()

    if not chat_ids:
        logger.warning("No Telegram chat IDs are configured.")
        return False

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    overall_success = True

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        for chat_id in chat_ids:

            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            destination_success = False

            for attempt in range(1, MAX_RETRIES + 1):

                try:
                    async with session.post(
                        BASE_URL,
                        json=payload,
                    ) as response:

                        if response.status == 200:
                            destination_success = True

                            logger.info(
                                "Telegram message sent to %s.",
                                chat_id,
                            )

                            break

                        error_text = await response.text()

                        logger.error(
                            "Telegram error for %s "
                            "(attempt %s/%s): %s",
                            chat_id,
                            attempt,
                            MAX_RETRIES,
                            error_text,
                        )

                except asyncio.CancelledError:
                    raise

                except Exception:
                    logger.exception(
                        "Telegram request failed for %s "
                        "(attempt %s/%s).",
                        chat_id,
                        attempt,
                        MAX_RETRIES,
                    )

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_DELAY)

            if not destination_success:
                overall_success = False

                logger.error(
                    "Telegram message failed for destination %s.",
                    chat_id,
                )

    return overall_success


# =====================================================
# NEW SIGNAL
# =====================================================

async def send_signal(
    signal: dict[str, Any],
) -> bool:
    """
    Send a new trading signal.
    """

    message = format_signal(signal)

    return await send_message(message)


# =====================================================
# ENTRY HIT
# =====================================================

async def send_entry_hit(
    trade: dict[str, Any],
) -> bool:
    """
    Notify that trade entry has been reached.
    """

    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_entry(
        symbol,
        direction,
    )

    return await send_message(message)


# =====================================================
# TP1
# =====================================================

async def send_tp1_hit(
    trade: dict[str, Any],
) -> bool:
    """
    Notify that TP1 has been reached.
    """

    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_tp(
        symbol,
        direction,
        1,
        "2R",
    )

    return await send_message(message)


# =====================================================
# TP2
# =====================================================

async def send_tp2_hit(
    trade: dict[str, Any],
) -> bool:
    """
    Notify that TP2 has been reached.
    """

    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_tp(
        symbol,
        direction,
        2,
        "3R",
    )

    return await send_message(message)


# =====================================================
# STOP LOSS
# =====================================================

async def send_stop_loss(
    trade: dict[str, Any],
) -> bool:
    """
    Notify that stop loss has been triggered.
    """

    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_stop(
        symbol,
        direction,
    )

    return await send_message(message)


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven(
    trade: dict[str, Any],
) -> bool:
    """
    Notify that trade has closed at breakeven.
    """

    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_breakeven(
        symbol,
        direction,
    )

    return await send_message(message)


# =====================================================
# CUSTOM REPORT
# =====================================================

async def send_custom_report(
    title: str,
    report: dict[str, Any],
) -> bool:
    """
    Send performance statistics.
    """

    total = report.get("total", 0)
    wins = report.get("wins", 0)
    losses = report.get("losses", 0)
    breakevens = report.get("breakevens", 0)
    win_rate = report.get("win_rate", 0)
    total_rr = report.get("total_rr", 0)
    average_rr = report.get("average_rr", 0)

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

    return await send_message(message)


# =====================================================
# TEST CONNECTION
# =====================================================

async def send_test_message() -> bool:
    """
    Verify Telegram connectivity.
    """

    message = (
        "✅ *BLISSFINITY SIGNAL*\n\n"
        "Telegram connection successful.\n\n"
        "Bot is online and ready."
    )

    return await send_message(message)


# =====================================================
# BOT STARTUP
# =====================================================

async def send_startup_message() -> bool:
    """
    Notify when the bot starts.
    """

    message = (
        "🚀 *BLISSFINITY SIGNAL*\n\n"
        "Production Version\n\n"
        "Scanner Started\n"
        "Trade Tracker Started\n\n"
        "Monitoring markets..."
    )

    return await send_message(message)


# =====================================================
# BOT SHUTDOWN
# =====================================================

async def send_shutdown_message() -> bool:
    """
    Notify when the bot stops.
    """

    message = (
        "🛑 *BLISSFINITY SIGNAL*\n\n"
        "Bot stopped.\n\n"
        "Monitoring paused."
    )

    return await send_message(message)


# =====================================================
# HEARTBEAT
# =====================================================

async def send_heartbeat() -> bool:
    """
    Send an optional system heartbeat.
    """

    message = (
        "💚 *Bot Status*\n\n"
        "System Online\n\n"
        "Scanner Running\n"
        "Trade Tracker Running\n\n"
        "No issues detected."
    )

    return await send_message(message)


# =====================================================
# WEEKLY REPORT
# =====================================================

async def send_weekly_report(
    report: dict[str, Any],
) -> bool:
    """
    Send weekly performance report.
    """

    return await send_custom_report(
        "Weekly Performance Report",
        report,
    )