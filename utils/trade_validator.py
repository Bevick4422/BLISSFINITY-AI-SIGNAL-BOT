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
    tp = float(signal["tp"])

    # -------------------------
    # BUY
    # -------------------------

    if direction == "BUY":

        if not (sl < entry < tp):

            logger.warning(
                "Invalid BUY trade rejected: %s",
                signal["symbol"],
            )

            return False

    # -------------------------
    # SELL
    # -------------------------

    elif direction == "SELL":

        if not (tp < entry < sl):

            logger.warning(
                "Invalid SELL trade rejected: %s",
                signal["symbol"],
            )

            return False

    # -------------------------
    # Duplicate Prices
    # -------------------------

    prices = [entry, sl, tp]

    if len(set(prices)) != len(prices):

        logger.warning(
            "Duplicate prices detected: %s",
            signal["symbol"],
        )

        return False

    return True