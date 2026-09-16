"""
Detect liquidity grabs.

Buy:
Current candle sweeps previous low
then closes back above it.

Sell:
Current candle sweeps previous high
then closes back below it.
"""


def detect_liquidity_grab(df):

    if len(df) < 3:
        return {
            "grab": None
        }

    prev = df.iloc[-2]
    cur = df.iloc[-1]

    # BUY liquidity sweep
    if cur["low"] < prev["low"] and cur["close"] > prev["low"]:
        return {
            "grab": "BUY"
        }

    # SELL liquidity sweep
    if cur["high"] > prev["high"] and cur["close"] < prev["high"]:
        return {
            "grab": "SELL"
        }

    return {
        "grab": None
    }
