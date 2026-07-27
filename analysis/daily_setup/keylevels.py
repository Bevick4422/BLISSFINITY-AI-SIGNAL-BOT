
"""
BLISSFINITY AI SIGNAL BOT
Key Level Detection
"""

LOOKBACK = 30


def find_v_shape(df):
    """
    Find the latest V-shape support.
    """

    candles = df.tail(LOOKBACK)

    for i in range(len(candles) - 2, 1, -1):

        left = candles.iloc[i - 1]
        mid = candles.iloc[i]
        right = candles.iloc[i + 1]

        if (
            mid["low"] < left["low"]
            and mid["low"] < right["low"]
            and right["close"] > right["open"]
        ):
            return float(mid["low"])

    return None


def find_a_shape(df):
    """
    Find the latest A-shape resistance.
    """

    candles = df.tail(LOOKBACK)

    for i in range(len(candles) - 2, 1, -1):

        left = candles.iloc[i - 1]
        mid = candles.iloc[i]
        right = candles.iloc[i + 1]

        if (
            mid["high"] > left["high"]
            and mid["high"] > right["high"]
            and right["close"] < right["open"]
        ):
            return float(mid["high"])

    return None