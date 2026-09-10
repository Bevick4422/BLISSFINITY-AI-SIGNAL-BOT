"""
=====================================================
BLISSFINITY SIGNAL
Discord Sender
Production Version
=====================================================
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp

from config.settings import DISCORD_WEBHOOK_URL


# =====================================================
# CONFIGURATION
# =====================================================

REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2

logger = logging.getLogger("Discord")


# =====================================================
# DISCORD COLORS
# =====================================================

BUY_COLOR = 0x2ECC71
SELL_COLOR = 0xE74C3C
INFO_COLOR = 0x5865F2


# =====================================================
# TEXT HELPERS
# =====================================================

def _extract(
    text: str,
    label: str,
) -> str | None:
    """
    Extract a single line value from a formatted
    signal message.

    Example:
        Entry: 0.497100
    """

    pattern = (
        rf"(?im)^\s*{re.escape(label)}\s*:\s*(.+?)\s*$"
    )

    match = re.search(
        pattern,
        text,
    )

    if not match:
        return None

    return match.group(1).strip()


def _clean_markdown(
    text: str,
) -> str:
    """
    Remove Telegram-style Markdown so Discord
    can format the message cleanly.
    """

    text = text.replace(
        "**",
        "",
    )

    text = text.replace(
        "__",
        "",
    )

    text = text.replace(
        "*",
        "",
    )

    text = text.replace(
        "`",
        "",
    )

    return text.strip()


def _is_signal(
    text: str,
) -> bool:
    """
    Detect whether the message is a trading signal.
    """

    normalized = text.upper()

    return (
        "BLISSFINITY SIGNAL" in normalized
        and (
            "DIRECTION:" in normalized
            or "ENTRY:" in normalized
        )
    )


# =====================================================
# SIGNAL EMBED
# =====================================================

def _build_signal_embed(
    text: str,
) -> dict[str, Any]:
    """
    Convert the existing signal text into a
    professional Discord trading embed.
    """

    symbol = _extract(
        text,
        "Symbol",
    ) or _extract(
        text,
        "Pair",
    ) or "UNKNOWN"

    direction = _extract(
        text,
        "Direction",
    ) or "UNKNOWN"

    entry = _extract(
        text,
        "Entry",
    )

    stop_loss = _extract(
        text,
        "Stop Loss",
    )

    tp1 = _extract(
        text,
        "TP1",
    )

    tp2 = _extract(
        text,
        "TP2",
    )

    rr = _extract(
        text,
        "RR",
    )

    confidence = _extract(
        text,
        "Confidence",
    )

    direction_upper = direction.upper()

    if direction_upper == "BUY":
        direction_icon = "🟢"
        color = BUY_COLOR

    elif direction_upper == "SELL":
        direction_icon = "🔴"
        color = SELL_COLOR

    else:
        direction_icon = "⚪"
        color = INFO_COLOR

    fields: list[dict[str, Any]] = []

    # -------------------------------------------------
    # ENTRY
    # -------------------------------------------------

    if entry:
        fields.append(
            {
                "name": "🎯 Entry",
                "value": f"`{entry}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # STOP LOSS
    # -------------------------------------------------

    if stop_loss:
        fields.append(
            {
                "name": "🛑 Stop Loss",
                "value": f"`{stop_loss}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # TAKE PROFIT 1
    # -------------------------------------------------

    if tp1:
        fields.append(
            {
                "name": "💰 Take Profit 1",
                "value": f"`{tp1}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # TAKE PROFIT 2
    # -------------------------------------------------

    if tp2:
        fields.append(
            {
                "name": "💰 Take Profit 2",
                "value": f"`{tp2}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # RISK / REWARD
    # -------------------------------------------------

    if rr:
        fields.append(
            {
                "name": "📊 Risk / Reward",
                "value": f"`1 : {rr.replace('R', '')}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # CONFIDENCE
    # -------------------------------------------------

    if confidence:
        fields.append(
            {
                "name": "💎 Confidence",
                "value": f"`{confidence}`",
                "inline": True,
            }
        )

    # -------------------------------------------------
    # FINAL EMBED
    # -------------------------------------------------

    embed = {
        "title": (
            f"🚨 BLISSFINITY SIGNAL • {symbol}"
        ),
        "description": (
            f"{direction_icon} "
            f"**{direction_upper}**"
        ),
        "color": color,
        "fields": fields,
        "footer": {
            "text": "BLISSFINITY SIGNAL SYSTEM",
        },
    }

    return embed


# =====================================================
# GENERAL EMBED
# =====================================================

def _build_general_embed(
    text: str,
) -> dict[str, Any]:
    """
    Convert non-signal notifications into a clean
    Discord embed.
    """

    cleaned = _clean_markdown(
        text
    )

    lines = [
        line.strip()
        for line in cleaned.splitlines()
        if line.strip()
    ]

    if lines:
        title = lines[0]
        description = "\n".join(
            lines[1:]
        )
    else:
        title = "BLISSFINITY SIGNAL"
        description = cleaned

    return {
        "title": title,
        "description": description,
        "color": INFO_COLOR,
        "footer": {
            "text": "BLISSFINITY SIGNAL SYSTEM",
        },
    }


# =====================================================
# BUILD DISCORD PAYLOAD
# =====================================================

def _build_payload(
    text: str,
) -> dict[str, Any]:
    """
    Build the Discord webhook payload.
    """

    if _is_signal(text):
        embed = _build_signal_embed(
            text
        )
    else:
        embed = _build_general_embed(
            text
        )

    return {
        "embeds": [
            embed
        ]
    }


# =====================================================
# DISCORD API
# =====================================================

async def send_message(
    text: str,
) -> bool:
    """
    Send a professionally formatted notification
    to the configured Discord webhook.

    Discord formatting is independent from Telegram.
    """

    if not DISCORD_WEBHOOK_URL:
        logger.warning(
            "Discord webhook URL is missing."
        )
        return False

    if not text or not text.strip():
        logger.warning(
            "Discord message is empty."
        )
        return False

    payload = _build_payload(
        text
    )

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):
        try:

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.post(
                    DISCORD_WEBHOOK_URL,
                    json=payload,
                ) as response:

                    if response.status in (
                        200,
                        204,
                    ):
                        logger.info(
                            "Discord message sent successfully."
                        )

                        return True

                    error_text = await response.text()

                    logger.error(
                        "Discord error "
                        "(attempt %s/%s): HTTP %s | %s",
                        attempt,
                        MAX_RETRIES,
                        response.status,
                        error_text,
                    )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Discord request failed "
                "(attempt %s/%s).",
                attempt,
                MAX_RETRIES,
            )

        if attempt < MAX_RETRIES:
            await asyncio.sleep(
                RETRY_DELAY
            )

    logger.error(
        "Discord message failed after %s attempts.",
        MAX_RETRIES,
    )

    return False


# =====================================================
# NEW SIGNAL
# =====================================================

async def send_signal(
    message: str,
) -> bool:
    """
    Send a new trading signal to Discord.
    """

    return await send_message(
        message
    )


# =====================================================
# TEST CONNECTION
# =====================================================

async def send_test_message() -> bool:
    """
    Verify Discord webhook connectivity.
    """

    message = (
        "🚨 BLISSFINITY SIGNAL\n\n"
        "Discord connection successful.\n\n"
        "Production notification system is online."
    )

    return await send_message(
        message
    )