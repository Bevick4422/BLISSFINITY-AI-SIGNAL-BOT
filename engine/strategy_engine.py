"""
============================================================
BLISSFINITY SIGNAL
Production Strategy Engine Ã¢â‚¬â€ Strategy-Aligned Integration
============================================================

MASTER FLOW

COMPLETED DAILY + H4
        |
        v
DAILY FIRST
        |
        +--> RANGE = NO SIGNAL
        |
        +--> DAILY ENGULFING
        |       -> direct continuation entry
        |       -> structural Daily SL
        |
        +--> DAILY V/A STRUCTURAL PATHWAY
                -> H4 Key Level / BOS
                -> full-body H4 BOS
                -> mandatory wick retest
                -> structural H4 SL
        |
        v
RISK
        -> TP1 = 2R
        -> TP2 = 3R
        |
        v
PRODUCTION SIGNAL
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from analysis.daily_structure.daily_structure_engine import detect_daily_setup
from analysis.h4_bos.h4_bos_engine import detect_h4_bos
from analysis.entry.break_retest import detect_break_retest
from analysis.risk.stoploss_engine import calculate_stop_loss
from engine.risk_engine import build_trade
from signal_engine.signal_builder import (
    build_signal as build_production_signal,
    validate_signal,
)

from analysis.candle_gate import get_completed_candles


MIN_DAILY_CANDLES = 8
MIN_H4_CANDLES = 12


def reject(reason: str) -> Optional[Dict[str, Any]]:
    print()
    print(f"RESULT: {reason}")
    return None


def validate_market_data(
    market_data: Dict[str, Any],
) -> bool:
    if not isinstance(market_data, dict):
        return False

    daily = market_data.get("1d")
    h4 = market_data.get("4h")

    if daily is None or h4 is None:
        return False

    if len(daily) < MIN_DAILY_CANDLES:
        return False

    if len(h4) < MIN_H4_CANDLES:
        return False

    return True


def get_current_price(h4) -> Optional[float]:
    try:
        if h4 is None or h4.empty:
            return None

        price = float(h4.iloc[-1]["close"])
    except (
        AttributeError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
    ):
        return None

    return price if price > 0 else None


def _normalise_setup_name(setup: Any) -> str:
    if setup is None:
        return ""

    return (
        str(setup)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def _get_setup_candle_index(
    daily_setup: Dict[str, Any],
    daily,
) -> Optional[int]:
    value = daily_setup.get("setup_candle_index")

    if value is None:
        value = daily_setup.get("level_index")

    if value is None:
        return None

    try:
        index = int(value)
    except (TypeError, ValueError):
        return None

    if index < 0 or index >= len(daily):
        return None

    return index


def _get_stop_reference(
    entry_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    if not isinstance(entry_data, dict):
        return None

    reference = entry_data.get("stop_reference")

    if not isinstance(reference, dict):
        return None

    return reference


def _build_final_signal(
    symbol: str,
    direction: str,
    setup: str,
    entry_type: str,
    entry: float,
    confidence: float,
    current_price: float,
    stop_df,
    stop_reference: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    # --------------------------------------------------------
    # STRUCTURAL STOP LOSS
    # --------------------------------------------------------
    stop_result = calculate_stop_loss(
        df=stop_df,
        entry=entry,
        direction=direction,
        stop_reference=stop_reference,
    )

    if not isinstance(stop_result, dict):
        return reject("INVALID STRUCTURAL STOP RESULT")

    if stop_result.get("valid") is not True:
        return reject(
            f"STRUCTURAL STOP FAILED: "
            f"{stop_result.get('reason', 'UNKNOWN')}"
        )

    stop_loss = stop_result.get("stop_loss")

    if stop_loss is None:
        return reject("NO VALID STRUCTURAL STOP")

    # --------------------------------------------------------
    # RISK / TARGETS
    # --------------------------------------------------------
    trade = build_trade(
        entry=entry,
        stop_loss=stop_loss,
        direction=direction,
        tp1_rr=2.0,
        tp2_rr=3.0,
    )

    if not isinstance(trade, dict) or trade.get("valid") is not True:
        return reject("RISK ENGINE RETURNED INVALID TRADE")

    print()
    print("[RISK]")
    print(f"Entry        : {trade['entry']}")
    print(f"Stop Loss    : {trade['stop_loss']}")
    print(f"Risk         : {trade['risk']}")
    print(f"TP1          : {trade['tp1']}")
    print(f"TP2          : {trade['tp2']}")
    print(f"RR           : {trade['rr']}")

    # --------------------------------------------------------
    # PRODUCTION SIGNAL BUILDER
    # --------------------------------------------------------
    signal = build_production_signal(
        symbol=symbol,
        direction=direction,
        setup=setup,
        entry=trade["entry"],
        stop_loss=trade["stop_loss"],
        tp1=trade["tp1"],
        tp2=trade["tp2"],
        confidence=float(confidence),
        entry_type=entry_type,
    )

    if signal is None:
        return reject("PRODUCTION SIGNAL BUILDER REJECTED TRADE")

    signal["current_price"] = current_price
    signal["risk_engine"] = True
    signal["production_signal"] = True
    signal["stop_reason"] = stop_result.get("reason")
    signal["stop_reference"] = stop_result.get("stop_reference")

    if not validate_signal(signal):
        return reject("FINAL SIGNAL VALIDATION FAILED")

    signal["status"] = "READY"

    print()
    print("=" * 60)
    print("PRODUCTION SIGNAL READY")
    print("=" * 60)
    print(f"Symbol       : {signal['symbol']}")
    print(f"Direction    : {signal['direction']}")
    print(f"Setup        : {signal['setup']}")
    print(f"Entry Type   : {signal['entry_type']}")
    print(f"Entry        : {signal['entry']}")
    print(f"Stop Loss    : {signal['stop_loss']}")
    print(f"TP1          : {signal['tp1']}")
    print(f"TP2          : {signal['tp2']}")
    print(f"Risk         : {signal['risk']}")
    print(f"RR           : {signal['rr']}")
    print(f"Confidence   : {signal['confidence']}")
    print("=" * 60)

    return signal


def evaluate_symbol(
    symbol: str,
    market_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Evaluate one symbol.

    Daily is evaluated first. H4 is only consulted after the Daily
    pathway has determined that H4 structure/entry is required.
    """
    print()
    print("=" * 60)
    print(f"{symbol} | STRATEGY ENGINE")
    print("=" * 60)

    if not validate_market_data(market_data):
        return reject("MARKET DATA INVALID")

    raw_daily = market_data["1d"]
    raw_h4 = market_data["4h"]

    # --------------------------------------------------------
    # COMPLETED-CANDLE GATE
    # --------------------------------------------------------
    try:
        daily = get_completed_candles(raw_daily, "1d")
        h4 = get_completed_candles(raw_h4, "4h")
    except Exception as exc:
        return reject(f"COMPLETED CANDLE GATE FAILED: {exc}")

    if len(daily) < MIN_DAILY_CANDLES:
        return reject("INSUFFICIENT COMPLETED DAILY DATA")

    if len(h4) < MIN_H4_CANDLES:
        return reject("INSUFFICIENT COMPLETED H4 DATA")

    current_price = get_current_price(h4)

    if current_price is None:
        return reject("CURRENT PRICE UNAVAILABLE")

    print(f"Current Price : {current_price}")
    print(f"Completed Daily candles : {len(daily)}")
    print(f"Completed H4 candles    : {len(h4)}")

    # --------------------------------------------------------
    # DAILY FIRST
    # --------------------------------------------------------
    daily_setup = detect_daily_setup(daily)

    if not isinstance(daily_setup, dict):
        return reject("DAILY ENGINE RETURNED INVALID RESULT")

    if daily_setup.get("valid") is not True:
        return reject(
            daily_setup.get("reason", "DAILY SETUP INVALID")
        )

    trend = daily_setup.get("trend")
    setup = daily_setup.get("setup")
    direction = daily_setup.get("direction")

    print()
    print("[1] DAILY")
    print(f"Trend        : {trend}")
    print(f"Setup        : {setup}")
    print(f"Direction    : {direction}")
    print(f"Level        : {daily_setup.get('level')}")
    print(f"Level Index  : {daily_setup.get('level_index')}")

    setup_name = _normalise_setup_name(setup)

    # --------------------------------------------------------
    # DAILY ENGULFING IS A STANDALONE CONTINUATION SETUP
    # --------------------------------------------------------
    # Daily Engulfing does NOT require the structural trend
    # classifier to establish HH/HL or LL/LH first.
    #
    # Therefore RANGE must NOT reject a valid Daily Engulfing.
    # The RANGE gate is applied only to structural V/A setups.
    # --------------------------------------------------------
    if setup_name in (
        "bullish engulfing",
        "bearish engulfing",
    ):
        daily_entry = daily_setup.get("entry")

        if daily_entry is None:
            # Strategy permits current market price when detection occurs.
            daily_entry = current_price

        try:
            entry = float(daily_entry)
        except (TypeError, ValueError):
            return reject("INVALID DAILY ENGULFING ENTRY")

        setup_index = _get_setup_candle_index(
            daily_setup,
            daily,
        )

        if setup_index is None:
            return reject(
                "DAILY ENGULFING SETUP CANDLE INDEX MISSING"
            )

        stop_reference = {
            "type": "DAILY_ENGULFING_WICK",
            "candle_index": setup_index,
        }

        print()
        print("[2] H4 BOS")
        print("H4 BOS       : NOT REQUIRED")

        print()
        print("[3] ENTRY")
        print("Entry Type   : ENGULFING")
        print(f"Entry        : {entry}")

        return _build_final_signal(
            symbol=symbol,
            direction=direction,
            setup=setup,
            entry_type="ENGULFING",
            entry=entry,
            confidence=90.0,
            current_price=current_price,
            stop_df=daily,
            stop_reference=stop_reference,
        )

    # --------------------------------------------------------
    # RANGE DOES NOT AUTOMATICALLY BLOCK STRUCTURAL SETUPS
    # --------------------------------------------------------
    # Structural V/A setups still require:
    # - A clear BUY/SELL direction
    # - Matching H4 BOS
    # - A valid mandatory break/retest
    # Unclear or conflicting setups remain NO SIGNAL.

    if direction not in ("BUY", "SELL"):
        return reject("DAILY SETUP HAS NO VALID DIRECTION")
    if setup_name not in (
        "v shape",
        "a shape",
    ):
        return reject("NO SUPPORTED DAILY STRUCTURAL PATHWAY")

    print()
    print("[2] H4 BOS")
    print("H4 BOS       : REQUIRED")

    bos = detect_h4_bos(h4)

    if not isinstance(bos, dict) or bos.get("bos") is not True:
        return reject(
            bos.get("reason", "WAITING FOR H4 BOS")
            if isinstance(bos, dict)
            else "WAITING FOR H4 BOS"
        )

    if bos.get("direction") != direction:
        return reject("H4 BOS DIRECTION DISAGREES WITH DAILY")

    key_level = bos.get("key_level", bos.get("broken_level"))
    key_level_index = bos.get("key_level_index")
    break_index = bos.get("break_index")

    if key_level is None:
        return reject("H4 KEY LEVEL MISSING")

    if key_level_index is None:
        return reject("H4 KEY LEVEL INDEX MISSING")

    if break_index is None:
        return reject("H4 BOS BREAK INDEX MISSING")

    print(f"BOS Direction : {bos.get('direction')}")
    print(f"Key Level     : {key_level}")
    print(f"Key Level Idx : {key_level_index}")
    print(f"BOS Index     : {break_index}")

    # --------------------------------------------------------
    # MANDATORY WICK RETEST
    # --------------------------------------------------------
    retest = detect_break_retest(
        df=h4,
        level=float(key_level),
        direction=direction,
        level_index=int(key_level_index),
        bos_index=int(break_index),
    )

    if not isinstance(retest, dict) or retest.get("valid") is not True:
        return reject(
            retest.get("reason", "NO REQUIRED H4 RETEST")
            if isinstance(retest, dict)
            else "NO REQUIRED H4 RETEST"
        )

    entry = retest.get("entry")

    if entry is None:
        return reject("RETEST HAS NO ENTRY PRICE")

    stop_reference = _get_stop_reference(retest)

    if stop_reference is None:
        stop_reference = {
            "type": "H4_KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": int(key_level_index),
        }

    print()
    print("[3] ENTRY")
    print(f"Entry Type   : BREAK_RETEST")
    print(f"Entry        : {entry}")
    print(f"Retest Index : {retest.get('retest_index')}")

    confidence = retest.get("confidence", 0)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    return _build_final_signal(
        symbol=symbol,
        direction=direction,
        setup=setup,
        entry_type="BREAK_RETEST",
        entry=float(entry),
        confidence=confidence,
        current_price=current_price,
        stop_df=h4,
        stop_reference=stop_reference,
    )


__all__ = [
    "evaluate_symbol",
    "validate_market_data",
    "get_current_price",
]

