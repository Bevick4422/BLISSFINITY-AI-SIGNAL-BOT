
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

from telegram.formatter import format_signal

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
                timeout=timeout,
            ) as session:

                async with session.post(
                    BASE_URL,
                    json=payload,
                ) as response:

                    if response.status == 200:

                        return True

                    logger.error(
                        "Telegram Error (%s/%s): %s",
                        attempt + 1,
                        MAX_RETRIES,
                        await response.text(),
                    )

        except Exception:

            logger.exception(
                "Telegram request failed (%s/%s)",
                attempt + 1,
                MAX_RETRIES,
            )

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
    Trade entry filled.
    """

    return await send_message(
        f"""
🟢 *ENTRY HIT*

*Pair:* `{trade["symbol"]}`

*Direction:* *{trade["direction"]}*

Entry Filled

Trade is now *ACTIVE*.
"""
    )


# =====================================================
# TP1
# =====================================================

async def send_tp1_hit(
    trade: dict,
) -> bool:
    """
    First target reached.
    """

    return await send_message(
        f"""
🎯 *TP1 HIT*

*Pair:* `{trade["symbol"]}`

*Direction:* *{trade["direction"]}*

✅ 50% Position Closed

🔒 Stop Loss moved to Breakeven
"""
    )
# =====================================================
# TP2
# =====================================================

async def send_tp2_hit(
    trade: dict,
) -> bool:
    """
    Final target reached.
    """

    return await send_message(
        f"""
🏆 *TP2 HIT*

*Pair:* `{trade["symbol"]}`

*Direction:* *{trade["direction"]}*

✅ Remaining Position Closed

🎉 Trade Closed

Result: *WIN*
"""
    )


# =====================================================
# STOP LOSS
# =====================================================

async def send_stop_loss(
    trade: dict,
) -> bool:
    """
    Stop loss triggered.
    """

    return await send_message(
        f"""
❌ *STOP LOSS*

*Pair:* `{trade["symbol"]}`

*Direction:* *{trade["direction"]}*

Trade Closed.

Result: *LOSS*
"""
    )


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven(
    trade: dict,
) -> bool:
    """
    Trade closed at breakeven.
    """

    return await send_message(
        f"""
⚪ *BREAKEVEN*

*Pair:* `{trade["symbol"]}`

*Direction:* *{trade["direction"]}*

Trade Closed.

Result: *BREAKEVEN*
"""
    )


# =====================================================
# DAILY REPORT
# =====================================================

async def send_daily_report(
    report: dict,
) -> bool:
    """
    Send daily performance report.
    """

    return await send_message(
        f"""
📊 *DAILY REPORT*

Signals: *{report['total']}*

Wins: *{report['wins']}*

Losses: *{report['losses']}*

Breakevens: *{report['breakevens']}*

Win Rate: *{report['win_rate']:.2f}%*

Net R: *{report['total_rr']:.2f}R*

Average R: *{report['average_rr']:.2f}R*
"""
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

    return await send_message(
        f"""
📈 *WEEKLY REPORT*

Trades: *{report['total']}*

Wins: *{report['wins']}*

Losses: *{report['losses']}*

Breakevens: *{report['breakevens']}*

Win Rate: *{report['win_rate']:.2f}%*

Net R: *{report['total_rr']:.2f}R*

Average R: *{report['average_rr']:.2f}R*
"""
    )
# =====================================================
# MONTHLY REPORT
# =====================================================

async def send_monthly_report(
    report: dict,
) -> bool:
    """
    Send monthly performance report.
    """

    return await send_message(
        f"""
🏆 *MONTHLY REPORT*

Trades: *{report['total']}*

Wins: *{report['wins']}*

Losses: *{report['losses']}*

Breakevens: *{report['breakevens']}*

Win Rate: *{report['win_rate']:.2f}%*

Net R: *{report['total_rr']:.2f}R*

Average R: *{report['average_rr']:.2f}R*
"""
    )


# =====================================================
# CUSTOM REPORT
# =====================================================

async def send_custom_report(
    title: str,
    report: dict,
) -> bool:
    """
    Send any statistics report.
    """

    return await send_message(
        f"""
📊 *{title}*

Trades: *{report.get("total", 0)}*

Wins: *{report.get("wins", 0)}*

Losses: *{report.get("losses", 0)}*

Breakevens: *{report.get("breakevens", 0)}*

Win Rate: *{report.get("win_rate", 0):.2f}%*

Net R: *{report.get("total_rr", 0):.2f}R*

Average R: *{report.get("average_rr", 0):.2f}R*
"""
    )


# =====================================================
# TEST CONNECTION
# =====================================================

async def send_test_message() -> bool:
    """
    Verify Telegram connectivity.
    """

    return await send_message(
        """
✅ *BLISSFINITY SIGNAL*

Telegram connection successful.

Bot is online and ready.
"""
    )


# =====================================================
# BOT STARTUP
# =====================================================

async def send_startup_message() -> bool:
    """
    Notify when the bot starts.
    """

    return await send_message(
        """
🚀 *BLISSFINITY SIGNAL*

Production Version

Scanner Started

Trade Tracker Started

Monitoring markets...
"""
    )


# =====================================================
# BOT SHUTDOWN
# =====================================================

async def send_shutdown_message() -> bool:
    """
    Notify when the bot stops.
    """

    return await send_message(
        """
🛑 *BLISSFINITY SIGNAL*

Bot stopped.

Monitoring paused.
"""
    )


# =====================================================
# HEARTBEAT
# =====================================================

async def send_heartbeat() -> bool:
    """
    Optional daily heartbeat.
    """

    return await send_message(
        """
💚 *Bot Status*

System Online

Scanner Running

Trade Tracker Running

No issues detected.
"""
    )