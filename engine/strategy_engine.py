
"""
=====================================================
BLISSFINITY AI SIGNAL BOT
Production Strategy Engine v9
=====================================================

Trading Pipeline

Market Data
    ↓
Market Validation
    ↓
Market Regime Filter
    ↓
Daily Bias
    ↓
Daily Setup Detection
    ↓
Daily Confirmation
    ↓
Save Daily Rejection Setup
    ↓
Wait For H4 BOS
    ↓
Entry Selection
    ↓
Stop Loss Engine
    ↓
Risk Engine
    ↓
Confluence Score
    ↓
Signal Builder
=====================================================
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Optional

# =====================================================
# DAILY ANALYSIS
# =====================================================

from analysis.daily_setup.daily_engine import (
    detect_daily_setup,
)

from engine.daily_bias import (
    get_daily_bias,
)

from engine.detectors.daily_engulfing import (
    detect_daily_engulfing_signal,
)

from engine.detectors.daily_rejection import (
    detect_daily_rejection_signal,
)

# =====================================================
# MARKET STRUCTURE
# =====================================================

from analysis.bos.bos_engine import (
    bullish_bos,
    bearish_bos,
)

# =====================================================
# ENTRY ENGINE
# =====================================================

from analysis.entry.entry_selector import (
    select_best_entry,
)

# =====================================================
# RISK
# =====================================================

from analysis.risk.stoploss_engine import (
    calculate_stop_loss,
)

# =====================================================
# SIGNAL
# =====================================================

from engine.signal_builder import (
    build_signal,
)

# =====================================================
# SETUP STORAGE
# =====================================================

from analysis.setup_manager.setup_manager import (
    get_setup,
    add_setup,
    remove_setup,
)

DEBUG = True
# =====================================================
# MARKET VALIDATION
# =====================================================

def validate_market(
    market: Dict[str, Any],
) -> bool:
    """
    Validate downloaded market data.
    """

    if not isinstance(market, dict):
        return False

    required = ("1d", "4h")

    for tf in required:

        if tf not in market:
            return False

        if market[tf] is None:
            return False

        if len(market[tf]) < 20:
            return False

    return True


# =====================================================
# MARKET REGIME
# =====================================================

def detect_market_regime(h4) -> str:
    """
    Detect overall market condition.

    Returns

        TRENDING
        RANGING
        HIGH_VOLATILITY
    """

    recent = h4.tail(20)

    highest = recent["high"].max()
    lowest = recent["low"].min()

    movement = highest - lowest

    average_range = (
        (recent["high"] - recent["low"])
        .mean()
    )

    if average_range == 0:

        return "RANGING"

    ratio = movement / average_range

    if ratio >= 5:

        return "TRENDING"

    if ratio <= 2:

        return "RANGING"

    return "HIGH_VOLATILITY"


# =====================================================
# SETUP VALIDATION
# =====================================================

def validate_setup(
    setup: Dict[str, Any],
) -> bool:

    if setup is None:

        return False

    required = (

        "symbol",

        "direction",

        "setup",

        "status",

        "level",

    )

    return all(

        key in setup

        for key in required

    )
# =====================================================
# CREATE DAILY SETUP
# =====================================================

def create_daily_setup(
    symbol: str,
    daily,
    bias: str,
) -> Optional[Dict[str, Any]]:
    """
    Analyse the daily timeframe.

    Flow

        Detect Daily Setup
              │
              ├── Daily Engulfing
              │       │
              │       ▼
              │   Immediate Signal
              │
              └── Daily Rejection
                      │
                      ▼
                 Save Setup
    """

    result = detect_daily_setup(daily)

    if result is None:
        return None

    if not result.get("valid", False):
        return None

    if DEBUG:

        print("\n" + "=" * 60)
        print(symbol)
        print("=" * 60)
        print(f"Bias  : {bias}")
        print(f"Setup : {result.get('setup')}")
        print(f"Level : {result.get('level')}")
        print("=" * 60)

        # =================================================
    # DAILY ENGULFING
    # =================================================

    engulfing = detect_daily_engulfing_signal(result)

    if engulfing is not None:

        # Entry price is the close of the confirmed
        # Daily Engulfing candle.

        entry_price = float(
            daily.iloc[-1]["close"]
        )

        signal = build_signal(

            symbol=symbol,

            direction=engulfing["direction"],

            setup=result["setup"],

            candle=daily.iloc[-1],

            entry=entry_price,

            entry_type="ENGULFING",

        )

        if signal is None:

            if DEBUG:
                print(
                    f"{symbol} | Failed To Build Daily Engulfing Signal"
                )

            return None

        if DEBUG:
            print(
                f"{symbol} | Daily Engulfing Signal Generated"
            )

        return signal

    # =================================================
    # DAILY REJECTION
    # =================================================

    rejection = detect_daily_rejection_signal(result)

    if rejection is None:
        return None

    setup_data = {

        "symbol": symbol,

        "direction": rejection["direction"],

        "setup": result["setup"],

        "status": "WAITING_FOR_BOS",

        "method": "DAILY_REJECTION",

        "level": float(result["level"]),

        "bos": False,

        "signal_sent": False,

        "created_at": None,

    }

    add_setup(setup_data)

    print(f"{symbol} | Daily Rejection Saved")

    return None
# =====================================================
# EVALUATE SYMBOL
# =====================================================

def evaluate_symbol(
    symbol: str,
    market: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Main strategy evaluation.

    Flow

    Validate Market
          ↓
    Market Regime
          ↓
    Daily Bias
          ↓
    Existing Setup?
          ↓
          ├── No
          │      ↓
          │  Create Daily Setup
          │
          └── Yes
                 ↓
              Wait BOS
                 ↓
             Entry Engine
                 ↓
             Stop Loss
                 ↓
             Build Signal
    """

    try:

        # =================================================
        # VALIDATE MARKET
        # =================================================

        if not validate_market(market):

            if DEBUG:
                print(f"{symbol} | Invalid Market Data")

            return None

        daily = market["1d"]
        h4 = market["4h"]

        # =================================================
        # MARKET REGIME FILTER
        # =================================================

        regime = detect_market_regime(h4)

        if regime == "RANGING":

            if DEBUG:
                print(f"{symbol} | Market Ranging")

            return None

        # =================================================
        # DAILY BIAS
        # =================================================

        bias = get_daily_bias(daily)

        if DEBUG:
            print(f"{symbol} | Bias : {bias}")

        # =================================================
        # LOAD SETUP
        # =================================================

        setup = get_setup(symbol)

        if setup is not None:

            if not validate_setup(setup):

                remove_setup(symbol)

                return None

        # =================================================
        # CREATE NEW SETUP
        # =================================================

        if setup is None:

            return create_daily_setup(

                symbol=symbol,

                daily=daily,

                bias=bias,

            )

        # =================================================
        # WAITING FOR BOS
        # =================================================

        if setup["status"] != "WAITING_FOR_BOS":

            remove_setup(symbol)

            return None

        direction = setup["direction"]

        # =================================================
        # BOS CONFIRMATION
        # =================================================

        if direction == "BUY":

            bos = bullish_bos(h4)

        elif direction == "SELL":

            bos = bearish_bos(h4)

        else:

            remove_setup(symbol)

            return None

        if not bos:

            if DEBUG:
                print(f"{symbol} | Waiting For BOS")

            return None

        print(f"{symbol} | BOS Confirmed")

        # =================================================
        # ENTRY SELECTION
        # =================================================

        entry = select_best_entry(

            df=h4,

            level=setup["level"],

            direction=direction,

        )

        if not entry:

            return None

        if not entry["entry_data"]["valid"]:

            return None

        print(
            f"{symbol} | Entry : "
            f"{entry['entry_type']}"
        )

        # =================================================
        # ATR
        # =================================================

        true_range = (

            h4["high"] - h4["low"]

        ).rolling(14).mean()

        atr = float(true_range.iloc[-1])

        # =================================================
        # STOP LOSS
        # =================================================

        stop = calculate_stop_loss(

            df=h4,

            atr=atr,

            direction=direction,

            entry_type=entry["entry_type"],

        )

        if not stop["valid"]:

            return None

        print(
            f"{symbol} | Stop : "
            f"{stop['stop_loss']}"
        )
        # =================================================
        # BUILD SIGNAL
        # =================================================

        signal = build_signal(

            symbol=symbol,

            direction=direction,

            setup=setup["setup"],

            candle=h4.iloc[-1],

            entry=entry.get("entry_price"),

            entry_type=entry["entry_type"],

            stop_loss=stop["stop_loss"],

        )

        if signal is None:

            if DEBUG:
                print(f"{symbol} | Signal Build Failed")

            return None

        # =================================================
        # CONFLUENCE SCORE
        # =================================================

        score = 0

        # BOS Confirmed
        score += 25

        # Market Trending
        if regime == "TRENDING":
            score += 20

        # Entry Quality
        entry_scores = {
            "LEFT_SHOULDER": 35,
            "BREAK_RETEST": 30,
            "FRESH_LEVEL": 25,
            "ENGULFING": 15,
        }

        score += entry_scores.get(
            entry["entry_type"],
            0,
        )

        # Daily Bias Exists
        if bias in ("BUY", "SELL"):
            score += 20

        signal["confidence"] = min(score, 100)

        # =================================================
        # CLEANUP
        # =================================================

        remove_setup(symbol)

        if DEBUG:

            print("=" * 60)
            print(f"{symbol} | SIGNAL GENERATED")
            print(f"Direction  : {direction}")
            print(f"Entry Type : {entry['entry_type']}")
            print(f"Confidence : {signal['confidence']}%")
            print("=" * 60)

        return signal

    except Exception as e:

        print("\n" + "=" * 60)
        print("STRATEGY ENGINE ERROR")
        print("=" * 60)
        print(f"Symbol : {symbol}")
        print(f"Error  : {e}")
        traceback.print_exc()
        print("=" * 60)

        return None