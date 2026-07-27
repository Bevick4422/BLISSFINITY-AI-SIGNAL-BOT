
"""
BLISSFINITY SIGNAL
TELEGRAM MESSAGE FORMATTER
"""

from datetime import datetime


def format_signal(signal: dict) -> str:
    """
    Format a new trading signal.
    """

    return f"""
🚨 *BLISSFINITY SIGNAL*

📈 Pair:
{signal["pair"]}

{"🟢" if signal["side"].upper() == "BUY" else "🔴"} Direction:
{signal["side"]}

🎯 Entry:
{signal["entry"]:.4f}

🛑 Stop Loss:
{signal["stop_loss"]:.4f}

🥇 TP1:
{signal["tp1"]:.4f}

🥈 TP2:
{signal["tp2"]:.4f}

⚖ Risk : Reward
1:{signal["rr"]}

📊 Confidence
{signal.get("confidence", 80)}%

🕒 {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC
""".strip()


def format_entry(pair, side):
    return f"""
🟢 *ENTRY FILLED*

📈 Pair:
{pair}

{"🟢" if side.upper() == "BUY" else "🔴"} Direction:
{side}

Trade is now ACTIVE.
""".strip()


def format_tp(pair, side, level):
    return f"""
🎯 *TAKE PROFIT {level} HIT*

📈 Pair:
{pair}

{"🟢" if side.upper() == "BUY" else "🔴"} Direction:
{side}

Congratulations! ✅
""".strip()


def format_stop(pair, side):
    return f"""
🛑 *STOP LOSS HIT*

📈 Pair:
{pair}

{"🟢" if side.upper() == "BUY" else "🔴"} Direction:
{side}

Risk managed.

Waiting for the next setup.
""".strip()