"""
Formats Telegram trading signals.
"""


def format_signal(signal):

    if signal is None:
        return ""

    direction = signal["direction"]

    emoji = "🟢" if direction == "BUY" else "🔴"

    text = f"""{emoji} {direction}

Pair:
{signal["pair"]}

Entry:
{signal["entry"]}

SL:
{signal["stop"]}

TP 1:
{signal["tp1"]}

TP 2:
{signal["tp2"]}

RR:
1 : {signal["rr"]}
"""

    return text
