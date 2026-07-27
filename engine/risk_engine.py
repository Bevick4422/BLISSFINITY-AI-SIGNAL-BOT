
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Risk Engine v7
=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Optional

# =====================================================
# DEFAULT RISK : REWARD
# =====================================================

DEFAULT_TP1_RR = 2.0
DEFAULT_TP2_RR = 3.0
DEFAULT_TP3_RR = 5.0


# =====================================================
# BUILD TRADE
# =====================================================

def build_trade(
    direction: str,
    candle,
    stop_loss: Optional[float] = None,
    entry: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Build a complete trade.

    Parameters
    ----------
    direction : str
        BUY or SELL

    candle :
        OHLC candle

    stop_loss : float | None
        Structure stop supplied by Stop Loss Engine.

    entry : float | None
        Custom entry price.

    Returns
    -------
    dict | None
    """

    try:

        close = float(candle["close"])
        high = float(candle["high"])
        low = float(candle["low"])

        if entry is None:
            entry = close

        entry = float(entry)

        # ---------------------------------------------
        # DEFAULT STOP LOSS
        # ---------------------------------------------

        if stop_loss is None:

            candle_range = high - low

            if candle_range <= 0:
                return None

            if direction == "BUY":

                stop_loss = entry - candle_range

            elif direction == "SELL":

                stop_loss = entry + candle_range

            else:

                return None

        stop_loss = float(stop_loss)

        # ---------------------------------------------
        # TRUE RISK
        # ---------------------------------------------

        risk = abs(entry - stop_loss)

        if risk <= 0:
            return None

        # ---------------------------------------------
        # TAKE PROFITS
        # ---------------------------------------------

        if direction == "BUY":

            tp1 = entry + risk * DEFAULT_TP1_RR
            tp2 = entry + risk * DEFAULT_TP2_RR
            tp3 = entry + risk * DEFAULT_TP3_RR

        elif direction == "SELL":

            tp1 = entry - risk * DEFAULT_TP1_RR
            tp2 = entry - risk * DEFAULT_TP2_RR
            tp3 = entry - risk * DEFAULT_TP3_RR

        else:

            return None

        # ---------------------------------------------
        # BUILD TRADE
        # ---------------------------------------------

        trade = {

            "entry": round(entry, 4),

            "stop_loss": round(stop_loss, 4),
            "sl": round(stop_loss, 4),

            "risk": round(risk, 4),

            "tp1": round(tp1, 4),
            "tp2": round(tp2, 4),
            "tp3": round(tp3, 4),

            "rr": DEFAULT_TP1_RR,

            "valid": True,

        }

        return trade

    except Exception as e:

        print("\n" + "=" * 60)
        print("RISK ENGINE ERROR")
        print("=" * 60)
        print(f"Error : {e}")
        traceback.print_exc()
        print("=" * 60)

        return None