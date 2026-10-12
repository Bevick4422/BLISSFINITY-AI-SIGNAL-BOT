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
        return "🟢"

    if direction == "SELL":
        return "🔴"

    return "⚪"


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

    symbol = signal.get("symbol") or signal.get("pair") or "UNKNOWN"
    target = signal.get("tp", signal.get("tp1", signal.get("tp2")))

    direction = (
        signal.get("direction")
        or signal.get("side")
        or ""
    )

    symbol = clean_symbol(symbol)

    return (
        "🚨 *BLISSFINITY SIGNAL*\n\n"

        "📈 *Pair*\n"
        f"`{symbol}`\n\n"

        f"{direction_emoji(direction)} *Direction*\n"
        f"{direction}\n\n"

        "🎯 *Entry*\n"
        f"`{signal['entry']:.6f}`\n\n"

        "🛑 *Stop Loss*\n"
        f"`{signal['stop_loss']:.6f}`\n\n"

        "🎯 *Take Profit*\n"
        f"`{float(target):.6f}`\n\n"

        "⚖️ *Risk : Reward*\n"
        f"1 : {signal.get('rr', 2)}\n\n"

        "📊 *Confidence*\n"
        f"{signal.get('confidence', 80)}%\n\n"

        f"🕒 {utc_time()}"
    )


# =====================================================
# ENTRY
# =====================================================

def format_entry(symbol: str, direction: str) -> str:
    symbol = clean_symbol(symbol) or "UNKNOWN"
    direction = str(direction or "UNKNOWN").upper()
    return (
        "\U0001F7E2 *ENTRY HIT*\n\n"
        f"\U0001F4C8 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade is now ACTIVE."
    )


# =====================================================
# TAKE PROFIT
# =====================================================

def format_tp(symbol: str, direction: str, rr: str = "2R") -> str:
    """Format the single final take-profit notification."""
    symbol = clean_symbol(symbol) or "UNKNOWN"
    direction = str(direction or "UNKNOWN").upper()
    return (
        "\U0001F3AF *TAKE PROFIT HIT*\n\n"
        f"\U0001F4C8 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n"
        f"\u2696\uFE0F Reward: *{rr}*\n\n"
        "Trade closed as a win."
    )


# =====================================================
# STOP LOSS
# =====================================================

def format_stop(symbol: str, direction: str) -> str:
    symbol = clean_symbol(symbol) or "UNKNOWN"
    direction = str(direction or "UNKNOWN").upper()
    return (
        "\U0001F534 *STOP LOSS HIT*\n\n"
        f"\U0001F4C8 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade closed."
    )


# =====================================================
# BREAKEVEN
# =====================================================

def format_breakeven(symbol: str, direction: str) -> str:
    symbol = clean_symbol(symbol) or "UNKNOWN"
    direction = str(direction or "UNKNOWN").upper()
    return (
        "\u26AA *BREAKEVEN*\n\n"
        f"\U0001F4C8 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade closed at break-even."
    )
