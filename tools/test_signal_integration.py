"""
=========================================================
BLISSFINITY SIGNAL BOT
Production Signal Integration Test
=========================================================

Tests:

    Market Data
        ↓
    ATR
        ↓
    Structure Stop
        ↓
    Risk Engine
        ↓
    Signal Builder
        ↓
    Signal Validation

This test uses controlled market data that contains
a valid BUY structure around the test entry.

It does NOT modify production modules.
"""

from __future__ import annotations

import pandas as pd

from analysis.atr.atr_engine import calculate_atr
from analysis.risk.stoploss_engine import calculate_stop_loss
from engine.risk_engine import build_trade
from engine.signal_builder import (
    build_signal,
    validate_signal,
    format_signal,
)


# =========================================================
# MARKET DATA
# =========================================================

def create_market_data() -> pd.DataFrame:
    """
    Create controlled BUY market data.

    The final candles trade around 100-105 while the
    structural low remains below the intended entry.
    """

    rows = []

    prices = [
        100.0,
        101.0,
        102.0,
        103.0,
        104.0,
        105.0,
        104.0,
        103.0,
        102.0,
        101.0,
        100.0,
        99.0,
        98.0,
        99.0,
        100.0,
        101.0,
        102.0,
        103.0,
        104.0,
        103.0,
    ]

    for price in prices:

        rows.append(
            {
                "open": price,
                "high": price + 2.0,
                "low": price - 2.0,
                "close": price + 0.5,
                "volume": 1000.0,
            }
        )

    return pd.DataFrame(rows)


# =========================================================
# TEST CANDLE
# =========================================================

def create_candle() -> dict:

    return {
        "open": 101.0,
        "high": 104.0,
        "low": 99.0,
        "close": 102.0,
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)
    print("BLISSFINITY SIGNAL | INTEGRATION TEST")
    print("=" * 70)

    market_data = create_market_data()

    candle = create_candle()

    direction = "BUY"
    setup = "V Shape"
    entry_type = "LEFT_SHOULDER"

    entry = 102.0
    confidence = 95.0

    # =====================================================
    # 1. ATR
    # =====================================================

    print()
    print("=" * 70)
    print("[1] ATR")
    print("=" * 70)

    atr = calculate_atr(
        market_data
    )

    print(
        f"ATR : {atr}"
    )

    if atr <= 0:

        print(
            "RESULT: ATR TEST FAILED"
        )

        return

    print(
        "RESULT: ATR SUCCESS"
    )

    # =====================================================
    # 2. STRUCTURE STOP
    # =====================================================

    print()
    print("=" * 70)
    print("[2] STRUCTURE STOP")
    print("=" * 70)

    stop_result = calculate_stop_loss(
        df=market_data,
        atr=atr,
        direction=direction,
        entry_type=entry_type,
    )

    print(
        f"Valid     : {stop_result.get('valid')}"
    )

    print(
        f"Stop Loss : {stop_result.get('stop_loss')}"
    )

    print(
        f"Reason    : {stop_result.get('reason')}"
    )

    if not stop_result.get("valid"):

        print(
            "RESULT: STRUCTURE STOP FAILED"
        )

        return

    stop_loss = float(
        stop_result["stop_loss"]
    )

    print(
        f"Entry     : {entry}"
    )

    # BUY stop must be below entry.

    if stop_loss >= entry:

        print()
        print(
            "RESULT: INVALID BUY STOP"
        )

        return

    print(
        "RESULT: STRUCTURE STOP SUCCESS"
    )

    # =====================================================
    # 3. RISK ENGINE
    # =====================================================

    print()
    print("=" * 70)
    print("[3] RISK ENGINE")
    print("=" * 70)

    trade = build_trade(
        direction=direction,
        candle=candle,
        entry=entry,
        stop_loss=stop_loss,
    )

    if trade is None:

        print(
            "RESULT: RISK ENGINE FAILED"
        )

        return

    print(
        f"Entry     : {trade['entry']}"
    )

    print(
        f"Stop Loss : {trade['stop_loss']}"
    )

    print(
        f"Risk      : {trade['risk']}"
    )

    print(
        f"TP1       : {trade['tp1']}"
    )

    print(
        f"TP2       : {trade['tp2']}"
    )

    print(
        f"TP3       : {trade['tp3']}"
    )

    print(
        f"RR        : {trade['rr']}"
    )

    print(
        "RESULT: RISK ENGINE SUCCESS"
    )

    # =====================================================
    # 4. SIGNAL BUILDER
    # =====================================================

    print()
    print("=" * 70)
    print("[4] SIGNAL BUILDER")
    print("=" * 70)

    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction=direction,
        setup=setup,
        candle_data=candle,
        entry=entry,
        entry_type=entry_type,
        market_data=market_data,
        confidence=confidence,
        stop_loss=stop_loss,
    )

    if signal is None:

        print(
            "RESULT: SIGNAL BUILDER FAILED"
        )

        return

    print()
    print(
        format_signal(signal)
    )

    # =====================================================
    # 5. VALIDATION
    # =====================================================

    print()
    print("=" * 70)
    print("[5] SIGNAL VALIDATION")
    print("=" * 70)

    valid = validate_signal(
        signal
    )

    print(
        f"Valid : {valid}"
    )

    if not valid:

        print(
            "RESULT: SIGNAL VALIDATION FAILED"
        )

        return

    # =====================================================
    # FINAL
    # =====================================================

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(
        "ALL SIGNAL INTEGRATION TESTS PASSED"
    )

    print()
    print("=" * 70)
    print("INTEGRATION TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":

    main()