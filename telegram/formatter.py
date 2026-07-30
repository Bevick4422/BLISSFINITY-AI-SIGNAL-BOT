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

    # Clean symbols like RUNE/USDT:USDT -> RUNE/USDT
    if symbol and ":USDT" in symbol:
        symbol = symbol.replace(":USDT", "")

    return (
        f"🚨 *BLISSFINITY*\n\n"
        f"📈 *Pair:* `{symbol}`\n"
        f"{direction_emoji(direction)} *Direction:* *{direction}*\n\n"
        f"💰 *Entry:* `{signal['entry']:.6f}`\n"
        f"🛑 *Stop Loss:* `{signal['stop_loss']:.6f}`\n\n"
        f"🎯 *TP1:* `{signal['tp1']:.6f}`\n"
        f"🎯 *TP2:* `{signal['tp2']:.6f}`\n\n"
        f"⚖️ *Risk : Reward:* 1:{signal.get('rr', 2)}\n"
        f"📊 *Confidence:* {signal.get('confidence', 80)}%\n\n"
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