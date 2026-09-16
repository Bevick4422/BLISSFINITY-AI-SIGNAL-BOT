"""
BLISSFINITY AI SIGNAL BOT
DAILY BOS / CHOCH ENGINE
"""


def detect_daily_bos(df):
    """
    Detect Daily Break of Structure (BOS)
    and Change of Character (CHOCH).
    """

    highs = df["high"].tail(6).tolist()
    lows = df["low"].tail(6).tolist()
    closes = df["close"].tail(6).tolist()

    previous_high = highs[-2]
    previous_low = lows[-2]

    current_close = closes[-1]

    bos = False
    choch = False
    direction = None
    level = None

    # ============================
    # Bullish BOS
    # ============================

    if current_close > previous_high:

        bos = True
        direction = "BUY"
        level = previous_high

    # ============================
    # Bearish BOS
    # ============================

    elif current_close < previous_low:

        bos = True
        direction = "SELL"
        level = previous_low

    # ============================
    # Change Of Character
    # ============================

    else:

        choch = True

    return {

        "bos": bos,

        "choch": choch,

        "direction": direction,

        "level": level

    }