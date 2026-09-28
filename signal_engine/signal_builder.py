"""
=========================================================
BLISSFINITY SIGNAL
Signal Builder
=========================================================

Purpose
-------
Convert a validated trade entry into a standardized
Blissfinity trading signal.

This module does NOT:

- Detect Daily setups
- Detect H4 BOS
- Detect market structure
- Select entries
- Detect liquidity
- Manage trades

Those responsibilities belong to the analysis pipeline.

This module ONLY:

1. Validates the trade structure.
2. Calculates risk.
3. Calculates reward.
4. Calculates R multiple.
5. Creates the final signal.
6. Validates completed signals.
7. Formats signals for Telegram/output.

Trade Structure
---------------

BUY:

    Stop Loss < Entry < TP

SELL:

    TP < Entry < Stop Loss

=========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ==========================================================
# SETTINGS
# ==========================================================

MIN_RISK = 0.0


# ==========================================================
# TIMESTAMP
# ==========================================================

def _now() -> str:
    """Return the current UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


# ==========================================================
# SAFE FLOAT
# ==========================================================

def _safe_float(
    value: Any,
) -> Optional[float]:
    """Safely convert a value to float."""

    try:

        if value is None:
            return None

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


# ==========================================================
# TRADE STRUCTURE VALIDATION
# ==========================================================

def _valid_trade_structure(
    direction: str,
    entry: float,
    stop_loss: float,
    tp: float,
) -> bool:
    """
    Validate the complete trade structure.

    BUY:

        SL < Entry < TP

    SELL:

        TP < Entry < SL
    """

    if direction == "BUY":

        return (
            stop_loss < entry < tp
        )

    if direction == "SELL":

        return (
            tp < entry < stop_loss
        )

    return False


# ==========================================================
# BUILD SIGNAL
# ==========================================================

def build_signal(
    symbol: str,
    direction: str,
    setup: str,
    entry: float,
    stop_loss: float,
    tp: float,
    confidence: float = 0.0,
    entry_type: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Build a complete trading signal.

    Returns
    -------
    dict
        Valid standardized signal.

    None
        When the trade structure is invalid.
    """

    # ------------------------------------------------------
    # BASIC TEXT VALIDATION
    # ------------------------------------------------------

    if not isinstance(
        symbol,
        str,
    ) or not symbol.strip():

        return None

    if not isinstance(
        setup,
        str,
    ) or not setup.strip():

        return None

    # ------------------------------------------------------
    # DIRECTION
    # ------------------------------------------------------

    direction = str(
        direction
    ).upper()

    if direction not in (
        "BUY",
        "SELL",
    ):

        return None

    # ------------------------------------------------------
    # NUMERIC VALUES
    # ------------------------------------------------------

    entry = _safe_float(
        entry
    )

    stop_loss = _safe_float(
        stop_loss
    )

    tp = _safe_float(
        tp
    )

    confidence = (
        _safe_float(
            confidence
        )
        or 0.0
    )

    # ------------------------------------------------------
    # REQUIRED VALUES
    # ------------------------------------------------------

    if (
        entry is None
        or stop_loss is None
        or tp is None
    ):

        return None

    # ------------------------------------------------------
    # CONFIDENCE RANGE
    # ------------------------------------------------------

    if confidence < 0:

        confidence = 0.0

    if confidence > 100:

        confidence = 100.0

    # ------------------------------------------------------
    # TRADE STRUCTURE
    # ------------------------------------------------------

    if not _valid_trade_structure(
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp=tp,
    ):

        return None

    # ------------------------------------------------------
    # RISK
    # ------------------------------------------------------

    risk = abs(
        entry - stop_loss
    )

    if risk <= MIN_RISK:

        return None

    # ------------------------------------------------------
    # REWARD
    # ------------------------------------------------------

    if direction == "BUY":

        reward = (
            tp - entry
        )

    else:

        reward = (
            entry - tp
        )

    if reward <= 0:

        return None

    # ------------------------------------------------------
    # R MULTIPLE
    # ------------------------------------------------------

    rr = reward / risk

    if rr <= 0:

        return None

    # ------------------------------------------------------
    # FINAL SIGNAL
    # ------------------------------------------------------

    return {
        "symbol": symbol,

        "direction": direction,

        "setup": setup,

        "entry_type": entry_type,

        "entry": entry,

        "stop_loss": stop_loss,

        "tp": tp,

        "risk": risk,

        "reward": reward,

        "rr": rr,

        "confidence": confidence,

        "valid": True,

        "status": "ACTIVE",

        "created_at": _now(),
    }


# ==========================================================
# VALIDATE SIGNAL
# ==========================================================

def validate_signal(
    signal: Dict[str, Any],
) -> bool:
    """
    Validate an already-created signal.

    This performs a second safety check before a signal
    is passed to Telegram, tracking, execution, or storage.
    """

    if not isinstance(
        signal,
        dict,
    ):

        return False

    if signal.get(
        "valid"
    ) is not True:

        return False

    symbol = signal.get(
        "symbol"
    )

    setup = signal.get(
        "setup"
    )

    direction = signal.get(
        "direction"
    )

    if not isinstance(
        symbol,
        str,
    ) or not symbol.strip():

        return False

    if not isinstance(
        setup,
        str,
    ) or not setup.strip():

        return False

    if direction not in (
        "BUY",
        "SELL",
    ):

        return False

    # ------------------------------------------------------
    # REQUIRED NUMERIC FIELDS
    # ------------------------------------------------------

    entry = _safe_float(
        signal.get("entry")
    )

    stop_loss = _safe_float(
        signal.get("stop_loss")
    )

    tp = _safe_float(
        signal.get("tp")
    )

    rr = _safe_float(
        signal.get("rr")
    )

    if (
        entry is None
        or stop_loss is None
        or tp is None
        or rr is None
    ):

        return False

    # ------------------------------------------------------
    # TRADE STRUCTURE
    # ------------------------------------------------------

    if not _valid_trade_structure(
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp=tp,
    ):

        return False

    # ------------------------------------------------------
    # RISK / REWARD
    # ------------------------------------------------------

    risk = abs(
        entry - stop_loss
    )

    if risk <= MIN_RISK:

        return False

    if rr <= 0:

        return False

    # ------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------

    confidence = _safe_float(
        signal.get(
            "confidence"
        )
    )

    if confidence is None:

        return False

    if not (
        0 <= confidence <= 100
    ):

        return False

    return True


# ==========================================================
# FORMAT SIGNAL
# ==========================================================

def format_signal(
    signal: Dict[str, Any],
) -> str:
    """
    Convert a valid signal into a readable message.
    """

    if not validate_signal(
        signal
    ):

        return "INVALID SIGNAL"

    return (
        "🚨 BLISSFINITY SIGNAL\n\n"

        f"Symbol: "
        f"{signal['symbol']}\n"

        f"Direction: "
        f"{signal['direction']}\n"

        f"Setup: "
        f"{signal['setup']}\n"

        f"Entry Type: "
        f"{signal.get('entry_type')}\n\n"

        f"Entry: "
        f"{signal['entry']}\n"

        f"Stop Loss: "
        f"{signal['stop_loss']}\n"

        f"TP: "
        f"{signal['tp']}\n\n"

        f"RR: "
        f"{signal['rr']:.2f}R\n"

        f"Confidence: "
        f"{signal['confidence']:.0f}%"
    )


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "build_signal",
    "validate_signal",
    "format_signal",
]