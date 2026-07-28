"""
=====================================================
BLISSFINITY AI SIGNAL BOT
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
    return "🟢" if direction.upper() == "BUY" else "🔴"


# =====================================================
# NEW SIGNAL
# =====================================================

def format_signal(signal: dict) -> str:

    symbol = signal.get("symbol") or signal.get("pair")
    direction = signal.get("direction") or signal.get("side")

    return (
        f"🚨 *BLISSFINITY AI SIGNAL*\n\n"
        f"📈 *Pair*\n"
        f"`{symbol}`\n\n"
        f"{direction_emoji(direction)} *Direction*\n"
        f"{direction}\n\n"
        f"🎯 *Entry*\n"
        f"`{signal['entry']:.6f}`\n\n"
        f"🛑 *Stop Loss*\n"
        f"`{signal['stop_loss']:.6f}`\n\n"
        f"🥇 *Take Profit 1*\n"
        f"`{signal['tp1']:.6f}`\n\n"
        f"🥈 *Take Profit 2*\n"
        f"`{signal['tp2']:.6f}`\n\n"
        f"⚖️ *Risk : Reward*\n"
        f"1 : {signal.get('rr', 2)}\n\n"
        f"📊 *Confidence*\n"
        f"{signal.get('confidence',80)}%\n\n"
        f"🕒 {utc_time()}"
    )


# =====================================================
# ENTRY
# =====================================================

def format_entry(symbol: str, direction: str) -> str:

    return (
        f"🟢 *ENTRY HIT*\n\n"
        f"📈 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade is now ACTIVE."
    )


# =====================================================
# TAKE PROFIT
# =====================================================

def format_tp(
    symbol: str,
    direction: str,
    level: int,
    rr: str,
) -> str:

    return (
        f"🎯 *TAKE PROFIT {level}*\n\n"
        f"📈 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n"
        f"⚖️ Reward: *{rr}*\n\n"
        "Excellent execution 🚀"
    )


# =====================================================
# STOP LOSS
# =====================================================

def format_stop(
    symbol: str,
    direction: str,
) -> str:

    return (
        f"🔴 *STOP LOSS HIT*\n\n"
        f"📈 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade closed."
    )


# =====================================================
# BREAKEVEN
# =====================================================

def format_breakeven(
    symbol: str,
    direction: str,
) -> str:

    return (
        f"⚪ *BREAKEVEN*\n\n"
        f"📈 Pair: `{symbol}`\n"
        f"{direction_emoji(direction)} Direction: *{direction}*\n\n"
        "Trade closed at break-even."
    )