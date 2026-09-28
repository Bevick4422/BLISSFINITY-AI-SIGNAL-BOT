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
from datetime import datetime, timezone
from typing import Any

import aiohttp
from discord.sender import send_message as send_discord_message

from config.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)

# Optional community chat ID.
# This allows the bot to work even when
# TELEGRAM_COMMUNITY_CHAT_ID is not defined
# in config/settings.py.
try:
    from config.settings import TELEGRAM_COMMUNITY_CHAT_ID
except ImportError:
    TELEGRAM_COMMUNITY_CHAT_ID = ""


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

    TELEGRAM_CHAT_ID is the primary destination.

    TELEGRAM_COMMUNITY_CHAT_ID is optional.

    Empty and duplicate chat IDs are removed.
    """

    chat_ids = [
        TELEGRAM_CHAT_ID,
        TELEGRAM_COMMUNITY_CHAT_ID,
    ]

    unique_chat_ids: list[str] = []

    for chat_id in chat_ids:

        if not chat_id:
            continue

        normalized_chat_id = str(
            chat_id
        ).strip()

        if not normalized_chat_id:
            continue

        if normalized_chat_id not in unique_chat_ids:
            unique_chat_ids.append(
                normalized_chat_id
            )

    return unique_chat_ids


# =====================================================
# TELEGRAM API
# =====================================================

async def send_message(
    text: str,
) -> bool:
    """
    Send one notification to all configured
    Telegram destinations and Discord.

    Telegram remains the primary delivery system.
    Discord is an additional notification destination.

    Discord failure does NOT cause Telegram
    notification delivery to be considered failed.
    """

    if not text or not text.strip():
        logger.warning(
            "Notification message is empty."
        )
        return False

    # =================================================
    # TELEGRAM
    # =================================================

    telegram_success = False

    if not TELEGRAM_TOKEN:
        logger.warning(
            "Telegram token is missing."
        )
    else:
        chat_ids = get_chat_ids()

        if not chat_ids:
            logger.warning(
                "No Telegram chat IDs are configured."
            )
        else:
            timeout = aiohttp.ClientTimeout(
                total=REQUEST_TIMEOUT
            )

            overall_telegram_success = True

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

                    for attempt in range(
                        1,
                        MAX_RETRIES + 1,
                    ):
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
                            await asyncio.sleep(
                                RETRY_DELAY
                            )

                    if not destination_success:
                        overall_telegram_success = False

                        logger.error(
                            "Telegram message failed "
                            "for destination %s.",
                            chat_id,
                        )

            telegram_success = (
                overall_telegram_success
            )

    # =================================================
    # DISCORD
    # =================================================

    try:
        discord_success = await send_discord_message(
            text
        )

        if discord_success:
            logger.info(
                "Discord notification delivered successfully."
            )
        else:
            logger.error(
                "Discord notification failed."
            )

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception(
            "Unexpected Discord notification error."
        )

    # =================================================
    # DELIVERY RESULT
    # =================================================

    # Telegram remains the primary success criterion.
    # Discord is an additional notification channel
    # and must never block the Telegram system.

    return telegram_success
# =====================================================
# NEW SIGNAL
# =====================================================

async def send_signal(
    signal: dict[str, Any],
) -> bool:
    """
    Send a new trading signal.
    """

    message = format_signal(
        signal
    )

    return await send_message(
        message
    )


# =====================================================
# ENTRY HIT
# =====================================================

async def send_entry_hit(
    trade: dict[str, Any],
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

    message = format_entry(
        symbol,
        direction,
    )

    return await send_message(
        message
    )


# =====================================================
# TAKE PROFIT
# =====================================================

async def send_tp_hit(
    trade: dict[str, Any],
) -> bool:
    symbol = trade.get("symbol", "UNKNOWN")
    direction = trade.get("direction", "UNKNOWN")

    message = format_tp(
        symbol,
        direction,
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

    symbol = trade.get(
        "symbol",
        "UNKNOWN",
    )

    direction = trade.get(
        "direction",
        "UNKNOWN",
    )

    message = format_stop(
        symbol,
        direction,
    )

    return await send_message(
        message
    )


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven(
    trade: dict[str, Any],
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

    message = format_breakeven(
        symbol,
        direction,
    )

    return await send_message(
        message
    )


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

    message = (
        "✅ *BLISSFINITY SIGNAL*\n\n"
        "Telegram connection successful.\n\n"
        "Bot is online and ready."
    )

    return await send_message(
        message
    )


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

    return await send_message(
        message
    )


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

    return await send_message(
        message
    )


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

    return await send_message(
        message
    )


# =====================================================
# WEEKLY REPORT
# =====================================================

async def send_weekly_report(
    report: dict[str, Any],
) -> bool:
    """
    Send the weekly bot performance recap.

    Closed trades contribute to the statistics.
    Ongoing trades are displayed in the trade log but
    excluded from the closed-book calculations.
    """

    gross_wins = float(report.get("gross_wins", 0.0))
    gross_losses = float(report.get("gross_losses", 0.0))
    net_closed = float(report.get("net_closed", 0.0))

    wins = int(report.get("wins", 0))
    losses = int(report.get("losses", 0))
    breakevens = int(report.get("breakevens", 0))
    win_rate = float(report.get("win_rate", 0.0))

    def format_r(value: float) -> str:
        if value == 0:
            return "0R"
        return f"{value:+g}R"

    def format_trade(item: dict[str, Any]) -> str:
        symbol = str(
            item.get("symbol", "UNKNOWN")
        ).split("/")[0]

        direction = str(
            item.get("direction", "")
        ).upper()

        if direction == "BUY":
            direction_text = "Long"
        elif direction == "SELL":
            direction_text = "Short"
        else:
            direction_text = direction.title()

        status = str(
            item.get("status", "PENDING")
        ).upper()

        if status == "WIN":
            outcome = "Tp=2R"
        elif status == "LOSS":
            outcome = "SL"
        elif status == "BREAKEVEN":
            outcome = "BE"
        elif status in {"OPEN", "PENDING", "BREAK_EVEN"}:
            outcome = "ongoing"
        else:
            outcome = status.lower()

        return (
            f"{symbol} {direction_text}="
            f"{outcome}"
        )

    day_names = {
        0: "MONDAY",
        1: "TUESDAY",
        2: "WEDNESDAY",
        3: "THURSDAY",
        4: "FRIDAY",
        5: "SATURDAY",
    }

    grouped: dict[str, list[str]] = {
        day: []
        for day in day_names.values()
    }

    for item in report.get("trade_log", []):
        created_at = item.get("created_at")

        if not created_at:
            continue

        try:
            created_time = datetime.fromisoformat(
                str(created_at)
            )

            if created_time.tzinfo is None:
                created_time = created_time.replace(
                    tzinfo=timezone.utc
                )

            day_name = day_names.get(
                created_time.weekday()
            )

        except (TypeError, ValueError):
            continue

        if day_name:
            grouped[day_name].append(
                format_trade(item)
            )

    lines = [
        "*Weekly Bot Performance Recap*",
        "",
        (
            f"Winners printed {format_r(gross_wins)}, "
            f"losses took {format_r(gross_losses)}, "
            f"so the closed book finished "
            f"{format_r(net_closed)}."
        ),
        "",
        "*Stats*",
        f"Gross wins: *{format_r(gross_wins)}*",
        f"Losses: *{format_r(gross_losses)}*",
        f"Net closed: *{format_r(net_closed)}*",
        f"Wins: *{wins}*",
        f"Losses: *{losses}*",
        f"Breakeven: *{breakevens}*",
        f"Win rate: *{win_rate:g}%*",
        "",
        "*Trade log*",
    ]

    for day_name in day_names.values():
        entries = grouped[day_name]

        if not entries:
            continue

        lines.append("")
        lines.append(f"*{day_name}*")

        for entry in entries:
            lines.append(entry)

    message = "\n".join(lines)

    return await send_message(message)


async def send_monthly_report(
    report: dict[str, Any],
) -> bool:
    """
    Send monthly performance report.
    """

    return await send_custom_report(
        "Monthly Performance Report",
        report,
    )
