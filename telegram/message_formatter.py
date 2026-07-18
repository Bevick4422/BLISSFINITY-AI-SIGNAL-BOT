def build_message(pair, direction, trade):

    icon = "🟢" if direction == "BUY" else "🔴"

    side = "LONG" if direction == "BUY" else "SHORT"

    return f"""
{icon} {side}

Pair: {pair}

Entry:
{trade['entry']}

SL:
{trade['stop']}

TP 1:
{trade['tp1']}

TP 2:
{trade['tp2']}

RR:
1 : {trade['rr']}
"""
