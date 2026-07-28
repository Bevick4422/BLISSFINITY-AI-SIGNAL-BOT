"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Telegram Sender
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
# SEND MESSAGE
# =====================================================

async def send_message(text: str) -> bool:
    """
    Send a Telegram Markdown message.
    """

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:

        logger.warning(
            "Telegram credentials are missing."
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

                        return True

                    error = await response.text()

                    logger.error(
                        "Telegram Error (%s/%s): %s",
                        attempt + 1,
                        MAX_RETRIES,
                        error,
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
# SIGNAL ALERT
# =====================================================

async def send_signal(signal: dict) -> bool:

    return await send_message(
        format_signal(signal)
    )


# =====================================================
# ENTRY HIT
# =====================================================

async def send_entry_message(
    pair: str,
    side: str,
) -> bool:

    return await send_message(
        f"""
🟢 *ENTRY HIT*

Pair: `{pair}`

Direction: *{side}*

The trade is now ACTIVE.
"""
    )


# =====================================================
# TAKE PROFIT
# =====================================================

async def send_tp_message(
    pair: str,
    side: str,
    tp: int,
    rr: str,
) -> bool:

    return await send_message(
        f"""
🎯 *TAKE PROFIT {tp}*

Pair: `{pair}`

Direction: *{side}*

Reward: *{rr}*

Excellent execution 🚀
"""
    )


# =====================================================
# STOP LOSS
# =====================================================

async def send_stop_message(
    pair: str,
    side: str,
) -> bool:

    return await send_message(
        f"""
🔴 *STOP LOSS*

Pair: `{pair}`

Direction: *{side}*

Trade closed.
"""
    )


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven_message(
    pair: str,
    side: str,
) -> bool:

    return await send_message(
        f"""
⚪ *BREAKEVEN*

Pair: `{pair}`

Direction: *{side}*

Trade closed at break-even.
"""
    )