"""
BLISSFINITY SIGNAL
Trade Validator
"""

import logging

logger = logging.getLogger("TradeValidator")


def validate_trade(signal: dict) -> bool:
    """
    Validate a trading signal before sending.
    """

    direction = signal["direction"].upper()

    entry = float(signal["entry"])
    sl = float(signal["stop_loss"])
    tp1 = float(signal["tp1"])
    tp2 = float(signal["tp2"])

    # -------------------------
    # BUY
    # -------------------------

    if direction == "BUY":

        if not (sl < entry < tp1 < tp2):

            logger.warning(
                "Invalid BUY trade rejected: %s",
                signal["symbol"],
            )

            return False

    # -------------------------
    # SELL
    # -------------------------

    elif direction == "SELL":

        if not (tp2 < tp1 < entry < sl):

            logger.warning(
                "Invalid SELL trade rejected: %s",
                signal["symbol"],
            )

            return False

    # -------------------------
    # Duplicate Prices
    # -------------------------

    prices = [entry, sl, tp1, tp2]

    if len(set(prices)) != len(prices):

        logger.warning(
            "Duplicate prices detected: %s",
            signal["symbol"],
        )

        return False

    return True