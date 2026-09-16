"""
BLISSFINITY ORDER BLOCK ENGINE

Detects fresh bullish and bearish order blocks.
"""


def detect_order_block(df):

    if len(df) < 5:
        return {
            "type": None,
            "high": None,
            "low": None
        }

    last = df.iloc[-2]

    # Bullish Order Block
    if (
        last["close"] < last["open"]
        and df.iloc[-1]["close"] > last["high"]
    ):

        return {
            "type": "BULLISH",
            "high": float(last["high"]),
            "low": float(last["low"])
        }

    # Bearish Order Block
    if (
        last["close"] > last["open"]
        and df.iloc[-1]["close"] < last["low"]
    ):

        return {
            "type": "BEARISH",
            "high": float(last["high"]),
            "low": float(last["low"])
        }

    return {
        "type": None,
        "high": None,
        "low": None
    }
