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

def _normalize_text(
    text: str,
) -> str:
    """
    Normalize Telegram/Discord formatting so the
    parser can reliably read the production signal.
    """

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    return text.strip()


def _clean_markdown(
    text: str,
) -> str:
    """
    Remove Telegram-style Markdown.
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


def _extract_value(
    text: str,
    label: str,
) -> str | None:
    """
    Extract values from both supported formats.

    Format 1:
        Entry: 0.492000

    Format 2:
        🎯 Entry
        0.492000
    """

    normalized = _normalize_text(
        text
    )

    # -------------------------------------------------
    # FORMAT 1
    # Label: Value
    # -------------------------------------------------

    pattern_colon = (
        rf"(?im)^\s*"
        rf"(?:[^\w\n]*)?"
        rf"{re.escape(label)}"
        rf"\s*:\s*(.+?)\s*$"
    )

    match = re.search(
        pattern_colon,
        normalized,
    )

    if match:
        return _clean_markdown(
            match.group(1)
        )

    # -------------------------------------------------
    # FORMAT 2
    # Label
    # Value
    # -------------------------------------------------

    pattern_separate = (
        rf"(?im)^\s*"
        rf"(?:[^\w\n]*)?"
        rf"{re.escape(label)}"
        rf"\s*$"
        rf"\n"
        rf"\s*(?:[^\w\n]*)?"
        rf"(.+?)"
        rf"\s*$"
    )

    match = re.search(
        pattern_separate,
        normalized,
    )

    if match:
        return _clean_markdown(
            match.group(1)
        )

    return None


def _extract_pair(
    text: str,
) -> str:
    """
    Extract the trading pair.
    """

    value = (
        _extract_value(
            text,
            "Symbol",
        )
        or _extract_value(
            text,
            "Pair",
        )
    )

    if value:
        return value

    # -------------------------------------------------
    # Fallback:
    # Search for a standard USDT pair.
    # -------------------------------------------------

    match = re.search(
        r"\b([A-Z0-9]{2,20}/USDT(?::USDT)?)\b",
        text.upper(),
    )

    if match:
        return match.group(1)

    return "UNKNOWN"


def _is_signal(
    text: str,
) -> bool:
    """
    Detect the actual production signal format.

    We deliberately support both:
        Direction: BUY

    and:

        Direction
        BUY
    """

    normalized = _normalize_text(
        text
    ).upper()

    has_signal_title = (
        "BLISSFINITY SIGNAL" in normalized
    )

    has_direction = (
        _extract_value(
            normalized,
            "Direction",
        )
        is not None
    )

    has_entry = (
        _extract_value(
            normalized,
            "Entry",
        )
        is not None
    )

    return (
        has_signal_title
        and (
            has_direction
            or has_entry
        )
    )


# =====================================================
# SIGNAL EMBED
# =====================================================

def _build_signal_embed(
    text: str,
) -> dict[str, Any]:
    """
    Convert the production signal message into
    the approved Discord embed format.
    """

    symbol = _extract_pair(
        text
    )

    direction = (
        _extract_value(
            text,
            "Direction",
        )
        or "UNKNOWN"
    )

    entry = _extract_value(
        text,
        "Entry",
    )

    stop_loss = _extract_value(
        text,
        "Stop Loss",
    )

    tp1 = _extract_value(
        text,
        "Take Profit 1",
    ) or _extract_value(
        text,
        "TP1",
    )

    tp2 = _extract_value(
        text,
        "Take Profit 2",
    ) or _extract_value(
        text,
        "TP2",
    )

    rr = _extract_value(
        text,
        "Risk / Reward",
    ) or _extract_value(
        text,
        "RR",
    )

    confidence = _extract_value(
        text,
        "Confidence",
    )

    direction_upper = (
        direction.upper()
    )

    # -------------------------------------------------
    # DIRECTION STYLE
    # -------------------------------------------------

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

        clean_rr = (
            rr
            .replace(
                "R",
                "",
            )
            .replace(
                "r",
                "",
            )
            .strip()
        )

        # Avoid producing "1 : 1 : 3".
        if ":" in clean_rr:

            rr_display = clean_rr

        else:

            rr_display = (
                f"1 : {clean_rr}"
            )

        fields.append(
            {
                "name": "📊 Risk / Reward",
                "value": f"`{rr_display}`",
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
    Format non-signal notifications.
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
    Build the correct Discord webhook payload.
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
    to Discord.
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