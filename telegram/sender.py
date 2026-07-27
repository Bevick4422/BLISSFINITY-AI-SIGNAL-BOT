
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Telegram Sender v8
=====================================================
"""

from __future__ import annotations

import asyncio
import traceback

import aiohttp

from config.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)

from telegram.formatter import format_signal


BASE_URL = (
    f"https://api.telegram.org/"
    f"bot{TELEGRAM_TOKEN}/sendMessage"
)

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3


# =====================================================
# SEND MESSAGE
# =====================================================

async def send_message(text: str) -> bool:
    """
    Send a Markdown message to Telegram.

    Returns
    -------
    bool
        True if sent successfully.
    """

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:

        print("Telegram is not configured.")

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

    for attempt in range(1, MAX_RETRIES + 1):

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

                    print(
                        f"Telegram Error "
                        f"(Attempt {attempt}): "
                        f"{error}"
                    )

        except Exception:

            print(
                f"Telegram Exception "
                f"(Attempt {attempt})"
            )

            traceback.print_exc()

        await asyncio.sleep(2)

    return False


# =====================================================
# NEW SIGNAL
# =====================================================

async def send_signal(signal) -> bool:

    text = format_signal(signal)

    return await send_message(text)


# =====================================================
# ENTRY HIT
# =====================================================

async def send_entry_message(
    pair: str,
    side: str,
) -> bool:

    text = (
        "🟢 *ENTRY HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n\n"
        "Trade is now LIVE."
    )

    return await send_message(text)


# =====================================================
# TAKE PROFIT
# =====================================================

async def send_tp_message(
    pair: str,
    side: str,
    tp: int,
    rr,
) -> bool:

    text = (
        f"🎯 *TP{tp} HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n"
        f"Risk : Reward: {rr}\n\n"
        "Congratulations! 🚀"
    )

    return await send_message(text)


# =====================================================
# STOP LOSS
# =====================================================

async def send_stop_message(
    pair: str,
    side: str,
) -> bool:

    text = (
        "🔴 *STOP LOSS HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n\n"
        "Trade Closed."
    )

    return await send_message(text)


# =====================================================
# BREAKEVEN
# =====================================================

async def send_breakeven_message(
    pair: str,
    side: str,
) -> bool:

    text = (
        "⚪ *BREAKEVEN*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n\n"
        "Trade closed at breakeven."
    )

    return await send_message(text)