"""
=====================================================
BLISSFINITY SIGNAL 
Telegram Formatter
=====================================================
"""

from __future__ import annotations

from datetime import UTC, datetime


# =====================================================
# TIME
# =====================================================

def utc_time() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


# =====================================================
# DIRECTION EMOJI
# =====================================================

def direction_emoji(direction: str) -> str:

    direction = direction.upper()

    if direction == "BUY":
        return "\U0001F7E2"

    if direction == "SELL":
        return "\U0001F534"

    return "\u26AA"


# =====================================================
# SYMBOL CLEANER
# =====================================================

def clean_symbol(symbol: str) -> str:

    if not symbol:
        return symbol

    return symbol.replace(":USDT", "")


# =====================================================
# NEW SIGNAL
# =====================================================

def format_signal(signal: dict) -> str:

    symbol = signal.get("symbol") or signal.get("pair")
    direction = signal.get("direction") or signal.get("side") or ""
    target = signal.get("tp", signal.get("tp1", signal.get("tp2")))
    symbol = clean_symbol(symbol)

    return (
        "\U0001F6A8 *BLISSFINITY SIGNAL*\n\n"
        "\U0001F4C8 *Pair*\n"
        f"`{symbol}`\n\n"
        f"{direction_emoji(direction)} *Direction*\n"
        f"{direction}\n\n"
        "\U0001F3AF *Entry*\n"
        f"`{signal['entry']:.6f}`\n\n"
        "\U0001F6D1 *Stop Loss*\n"
        f"`{signal['stop_loss']:.6f}`\n\n"
        "\U0001F3AF *Take Profit*\n"
        f"`{target:.6f}`\n\n"
        "\u2696\uFE0F *Risk : Reward*\n"
        f"1 : {signal.get('rr', 2)}\n\n"

        f"\U0001F552 {utc_time()}"
    )


# =====================================================
# ENTRY
# =====================================================

def format_entry(
    symbol: str,
    direction: str,
) -> str:

    symbol = clean_symbol(symbol)

    return (
        "ðŸŸ¢ *ENTRY HIT*\n\n"

        f"ðŸ“ˆ Pair: `{symbol}`\n"

        f"{direction_emoji(direction)} "
        f"Direction: *{direction}*\n\n"

        "Trade is now ACTIVE."
    )


# =====================================================
# TAKE PROFIT
# =====================================================

def format_tp(
    symbol: str,
    direction: str,
    rr: str = "2R",
) -> str:
    """Format the single final take-profit notification."""

    symbol = clean_symbol(symbol)

    return (
        "ðŸŽ¯ *TAKE PROFIT HIT*\n\n"
        f"ðŸ“ˆ Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n"
        f"âš–ï¸ Reward: *{rr}*\n\n"
        "Trade closed as a win."
    )


# =====================================================
# STOP LOSS
# =====================================================

def format_stop(
    symbol: str,
    direction: str,
) -> str:

    symbol = clean_symbol(symbol)

    return (
        "ðŸ”´ *STOP LOSS HIT*\n\n"

        f"ðŸ“ˆ Pair: `{symbol}`\n"

        f"{direction_emoji(direction)} "
        f"Direction: *{direction}*\n\n"

        "Trade closed."
    )


# =====================================================
# BREAKEVEN
# =====================================================

def format_breakeven(
    symbol: str,
    direction: str,
) -> str:

    symbol = clean_symbol(symbol)

    return (
        "âšª *BREAKEVEN*\n\n"

        f"ðŸ“ˆ Pair: `{symbol}`\n"

        f"{direction_emoji(direction)} "
        f"Direction: *{direction}*\n\n"

        "Trade closed at break-even."
    )