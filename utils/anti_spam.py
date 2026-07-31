"""
=====================================================
BLISSFINITY SIGNAL
Anti Spam Filter
=====================================================
"""

from datetime import datetime, timedelta
import logging

logger = logging.getLogger("AntiSpam")

# Stores the last signal sent for each symbol/direction
_last_signals = {}

# Cooldown period
COOLDOWN_HOURS = 6

# Entry price tolerance (0.1%)
ENTRY_TOLERANCE = 0.001


def is_duplicate_signal(signal: dict) -> bool:
    """
    Returns True if the signal is a duplicate.
    """

    symbol = signal["symbol"]
    direction = signal["direction"].upper()
    entry = float(signal["entry"])

    key = (symbol, direction)

    now = datetime.utcnow()

    if key in _last_signals:

        previous_entry, previous_time = _last_signals[key]

        difference = abs(entry - previous_entry) / entry

        if (
            difference <= ENTRY_TOLERANCE
            and now - previous_time < timedelta(hours=COOLDOWN_HOURS)
        ):

            logger.info(
                "Duplicate signal skipped: %s %s",
                symbol,
                direction,
            )

            return True

    _last_signals[key] = (
        entry,
        now,
    )

    return False