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
# DISCORD API
# =====================================================

async def send_message(
    text: str,
) -> bool:
    """
    Send a message to the configured Discord webhook.

    Returns True when Discord accepts the message.
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

    payload = {
        "content": text,
    }

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
        "🚨 **BLISSFINITY SIGNAL**\n\n"
        "✅ Discord connection successful.\n\n"
        "Production notification system is online."
    )

    return await send_message(
        message
    )