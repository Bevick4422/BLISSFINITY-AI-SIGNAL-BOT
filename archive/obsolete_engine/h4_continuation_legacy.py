"""
BLISSFINITY AI SIGNAL BOT
H4 Continuation Detector
"""


def detect_h4_continuation_signal(
    trend,
    at_key_level,
    engulfing
):
    """
    Generate an immediate continuation signal when:
    1. Higher timeframe trend is confirmed
    2. Price is at a key level
    3. An H4 engulfing candle forms
    """

    if trend not in ["BUY", "SELL"]:
        return None

    if not at_key_level:
        return None

    if engulfing != trend:
        return None

    return {
        "direction": trend,
        "method": "H4_CONTINUATION",
        "status": "READY",
        "signal": True,
    }