import pandas as pd


def detect_market_structure(df: pd.DataFrame):

    if len(df) < 10:
        return {
            "signal": "NONE"
        }

    highs = df["high"]
    lows = df["low"]

    last_high = highs.iloc[-2]
    prev_high = highs.iloc[-5]

    last_low = lows.iloc[-2]
    prev_low = lows.iloc[-5]

    if last_high > prev_high:

        return {
            "signal": "BOS_BULLISH"
        }

    elif last_low < prev_low:

        return {
            "signal": "BOS_BEARISH"
        }

    return {
        "signal": "NONE"
    }
