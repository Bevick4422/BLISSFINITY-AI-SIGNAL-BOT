
"""
BLISSFINITY AI SIGNAL BOT
TELEGRAM SENDER
"""

import aiohttp

from config.settings import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
)

from telegram.formatter import format_signal


BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


async def send_message(text):

    payload = {

        "chat_id": TELEGRAM_CHAT_ID,

        "text": text,

        "parse_mode": "Markdown"

    }

    try:

        async with aiohttp.ClientSession() as session:

            async with session.post(
                BASE_URL,
                json=payload
            ) as response:

                if response.status != 200:

                    print(
                        "Telegram Error:",
                        await response.text()
                    )

    except Exception as e:

        print("Telegram Exception:", e)


# ===================================
# NEW SIGNAL
# ===================================

async def send_signal(signal):

    text = format_signal(signal)

    await send_message(text)


# ===================================
# ENTRY HIT
# ===================================

async def send_entry_message(pair, side):

    text = (
        f"🟢 *ENTRY HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n\n"
        f"Trade is now LIVE."
    )

    await send_message(text)


# ===================================
# TP1
# ===================================

async def send_tp_message(pair, side, tp, rr):

    text = (
        f"🎯 *TAKE PROFIT {tp} HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n"
        f"RR: {rr}\n\n"
        f"Congratulations!"
    )

    await send_message(text)


# ===================================
# STOP LOSS
# ===================================

async def send_stop_message(pair, side):

    text = (
        f"🔴 *STOP LOSS HIT*\n\n"
        f"Pair: {pair}\n"
        f"Direction: {side}\n\n"
        f"Trade Closed."
    )

    await send_message(text)