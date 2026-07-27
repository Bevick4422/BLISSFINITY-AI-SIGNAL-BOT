
"""
=====================================================
BLISSFINITY SIGNAL BOT
Production Signal Builder v9
=====================================================
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from engine.risk_engine import build_trade

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE = 80


# =====================================================
# BUILD SIGNAL
# =====================================================

def build_signal(
    symbol: str,
    direction: str,
    setup: str,
    candle,
    entry: float,
    entry_type: str = "ENGULFING",
    stop_loss: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Build the final trading signal.
    """

    try:

        # ==========================================
        # VALIDATION
        # ==========================================

        if candle is None:

            logger.warning("%s | Candle is None", symbol)
            return None

        if entry is None:

            logger.warning("%s | Entry is None", symbol)
            return None

        # ==========================================
        # BUILD TRADE
        # ==========================================

        trade = build_trade(

            direction=direction,

            candle=candle,

            entry=float(entry),

            stop_loss=stop_loss,

        )

        if trade is None:

            logger.warning("%s | Trade build failed", symbol)
            return None

        # ==========================================
        # BUILD SIGNAL
        # ==========================================

        signal = {

            # Pair Information
            "symbol": symbol,
            "pair": symbol,

            # Direction
            "direction": direction,
            "side": direction,

            # Strategy
            "setup": setup,
            "entry_type": entry_type,

            # Prices
            "entry": round(float(entry), 4),
            "stop_loss": round(float(trade["stop_loss"]), 4),
            "tp1": round(float(trade["tp1"]), 4),
            "tp2": round(float(trade["tp2"]), 4),

            # Risk
            "rr": trade["rr"],

            # Confidence
            "confidence": DEFAULT_CONFIDENCE,

            # Status
            "status": "OPEN",
            "valid": True,

        }

        return signal

    except Exception:

        logger.exception(

            "Failed to build signal for %s",

            symbol,

        )

        return None