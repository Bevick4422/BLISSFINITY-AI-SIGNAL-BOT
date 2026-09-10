"""
=========================================================
BLISSFINITY SIGNAL
Production Signal -> Trade Tracker Integration Test
=========================================================

Pipeline:

    Market Data
        ↓
    Signal Builder
        ↓
    Signal Validation
        ↓
    Signal Formatting
        ↓
    Trade Tracker
        ↓
    TP1
        ↓
    TP2
        ↓
    WIN
        ↓
    Persistence
        ↓
    Performance
=========================================================
"""

from __future__ import annotations

import sys

import pandas as pd

from engine.signal_builder import (
    build_signal,
    validate_signal,
    format_signal,
)

from tracking.trade_tracker import (
    record_signal,
    get_trade,
    update_trade,
    get_performance,
)


TEST_SIGNAL_ID = "INTEGRATION_TEST_001"
TEST_SYMBOL = "TEST/BTC"


# =========================================================
# MARKET DATA
# =========================================================

def create_market_data() -> pd.DataFrame:

    rows = []

    for _ in range(39):

        rows.append(
            {
                "open": 100.0,
                "high": 102.0,
                "low": 98.0,
                "close": 100.0,
                "volume": 1000.0,
            }
        )

    rows.append(
        {
            "open": 100.0,
            "high": 102.0,
            "low": 98.0,
            "close": 101.0,
            "volume": 1000.0,
        }
    )

    return pd.DataFrame(rows)


# =========================================================
# SIGNAL CANDLE
# =========================================================

def create_candle() -> dict:

    return {
        "open": 100.0,
        "high": 102.0,
        "low": 98.0,
        "close": 101.0,
    }


# =========================================================
# DISPLAY SIGNAL
# =========================================================

def display_signal(signal) -> None:

    print()
    print("SIGNAL")
    print("-" * 60)

    if signal is None:

        print("Signal      : None")
        return

    fields = (
        "symbol",
        "direction",
        "setup",
        "entry_type",
        "entry",
        "stop_loss",
        "risk",
        "atr",
        "tp1",
        "tp2",
        "tp3",
        "rr",
        "confidence",
        "status",
        "valid",
        "created_at",
    )

    labels = {
        "symbol": "Symbol",
        "direction": "Direction",
        "setup": "Setup",
        "entry_type": "Entry Type",
        "entry": "Entry",
        "stop_loss": "Stop Loss",
        "risk": "Risk",
        "atr": "ATR",
        "tp1": "TP1",
        "tp2": "TP2",
        "tp3": "TP3",
        "rr": "RR",
        "confidence": "Confidence",
        "status": "Status",
        "valid": "Valid",
        "created_at": "Created At",
    }

    for field in fields:

        print(
            f"{labels[field]:12}: "
            f"{signal.get(field)}"
        )


# =========================================================
# DISPLAY TRADE
# =========================================================

def display_trade(trade) -> None:

    print()
    print("TRADE")
    print("-" * 60)

    if trade is None:

        print("Trade      : None")
        return

    fields = (
        "trade_id",
        "symbol",
        "direction",
        "entry",
        "stop_loss",
        "tp1",
        "tp2",
        "status",
        "tp1_hit",
        "tp2_hit",
        "sl_hit",
        "last_event",
        "result",
        "result_percent",
        "r_multiple",
    )

    labels = {
        "trade_id": "Trade ID",
        "symbol": "Symbol",
        "direction": "Direction",
        "entry": "Entry",
        "stop_loss": "Stop Loss",
        "tp1": "TP1",
        "tp2": "TP2",
        "status": "Status",
        "tp1_hit": "TP1 Hit",
        "tp2_hit": "TP2 Hit",
        "sl_hit": "SL Hit",
        "last_event": "Last Event",
        "result": "Result",
        "result_percent": "Result %",
        "r_multiple": "R Multiple",
    }

    for field in fields:

        print(
            f"{labels[field]:14}: "
            f"{trade.get(field)}"
        )


# =========================================================
# FAILURE HELPER
# =========================================================

def fail(message: str) -> bool:

    print()
    print(f"RESULT: {message}")

    return False


# =========================================================
# MAIN
# =========================================================

def main() -> bool:

    print()
    print("=" * 70)
    print(
        "BLISSFINITY SIGNAL | "
        "SIGNAL → TRADE TRACKER INTEGRATION TEST"
    )
    print("=" * 70)

    # =====================================================
    # 1. MARKET DATA
    # =====================================================

    print()
    print("=" * 70)
    print("[1] MARKET DATA")
    print("=" * 70)

    market_data = create_market_data()
    candle = create_candle()

    latest = market_data.iloc[-1]

    print(
        f"Market candles : {len(market_data)}"
    )

    print(
        f"Latest open    : {latest['open']}"
    )

    print(
        f"Latest high    : {latest['high']}"
    )

    print(
        f"Latest low     : {latest['low']}"
    )

    print(
        f"Latest close   : {latest['close']}"
    )

    if len(market_data) != 40:

        return fail(
            "MARKET DATA CANDLE COUNT INVALID"
        )

    if float(latest["close"]) != float(
        candle["close"]
    ):

        return fail(
            "MARKET DATA / CANDLE MISMATCH"
        )

    print(
        "RESULT: MARKET DATA SUCCESS"
    )

    # =====================================================
    # 2. SIGNAL BUILDER
    # =====================================================

    print()
    print("=" * 70)
    print("[2] SIGNAL BUILDER")
    print("=" * 70)

    signal = build_signal(

        symbol=TEST_SYMBOL,

        direction="BUY",

        setup="V Shape",

        candle_data=candle,

        entry=101.0,

        entry_type="LEFT_SHOULDER",

        market_data=market_data,

        confidence=95.0,

    )

    display_signal(signal)

    if signal is None:

        return fail(
            "SIGNAL BUILDER FAILED"
        )

    if not validate_signal(signal):

        return fail(
            "SIGNAL VALIDATION FAILED"
        )

    print()
    print(
        "RESULT: SIGNAL BUILDER SUCCESS"
    )

    # =====================================================
    # 3. SIGNAL FORMAT
    # =====================================================

    print()
    print("=" * 70)
    print("[3] SIGNAL FORMAT")
    print("=" * 70)

    formatted = format_signal(signal)

    print()
    print(formatted)

    if not formatted:

        return fail(
            "SIGNAL FORMAT RETURNED EMPTY RESULT"
        )

    if formatted == "INVALID SIGNAL":

        return fail(
            "SIGNAL FORMAT FAILED"
        )

    print()
    print(
        "RESULT: SIGNAL FORMAT SUCCESS"
    )

    # =====================================================
    # 4. RECORD TRADE
    # =====================================================

    print()
    print("=" * 70)
    print("[4] TRADE TRACKER")
    print("=" * 70)

    trade = record_signal(

        symbol=signal["symbol"],

        direction=signal["direction"],

        setup=signal["setup"],

        entry=signal["entry"],

        stop_loss=signal["stop_loss"],

        tp1=signal["tp1"],

        tp2=signal["tp2"],

        confidence=signal["confidence"],

        signal_id=TEST_SIGNAL_ID,

    )

    display_trade(trade)

    if trade is None:

        return fail(
            "TRADE RECORD FAILED"
        )

    if trade.get("status") != "OPEN":

        return fail(
            "NEW TRADE IS NOT OPEN"
        )

    trade_id = trade.get("trade_id")

    if not trade_id:

        return fail(
            "TRADE ID WAS NOT CREATED"
        )

    print()
    print(
        "RESULT: TRADE RECORDED SUCCESSFULLY"
    )

    # =====================================================
    # 5. TP1
    # =====================================================

    print()
    print("=" * 70)
    print("[5] TP1 TEST")
    print("=" * 70)

    trade = update_trade(

        trade_id,

        float(signal["tp1"]),

    )

    display_trade(trade)

    if trade is None:

        return fail(
            "TP1 UPDATE FAILED"
        )

    if not trade.get("tp1_hit"):

        return fail(
            "TP1 WAS NOT REGISTERED"
        )

    if trade.get("status") != "OPEN":

        return fail(
            "TRADE CLOSED PREMATURELY AT TP1"
        )

    print()
    print(
        "RESULT: TP1 HIT SUCCESSFULLY"
    )

    # =====================================================
    # 6. TP2
    # =====================================================

    print()
    print("=" * 70)
    print("[6] TP2 TEST")
    print("=" * 70)

    trade = update_trade(

        trade_id,

        float(signal["tp2"]),

    )

    display_trade(trade)

    if trade is None:

        return fail(
            "TP2 UPDATE FAILED"
        )

    if not trade.get("tp2_hit"):

        return fail(
            "TP2 WAS NOT REGISTERED"
        )

    if trade.get("status") != "CLOSED":

        return fail(
            "TRADE DID NOT CLOSE AT TP2"
        )

    if trade.get("result") != "WIN":

        return fail(
            "TRADE WAS NOT MARKED WIN"
        )

    print()
    print(
        "RESULT: TP2 HIT — TRADE CLOSED WIN"
    )

    # =====================================================
    # 7. PERSISTENCE
    # =====================================================

    print()
    print("=" * 70)
    print("[7] TRADE PERSISTENCE")
    print("=" * 70)

    saved_trade = get_trade(
        trade_id
    )

    display_trade(
        saved_trade
    )

    if saved_trade is None:

        return fail(
            "TRADE PERSISTENCE FAILED"
        )

    if saved_trade.get("status") != "CLOSED":

        return fail(
            "SAVED TRADE STATUS INVALID"
        )

    if saved_trade.get("result") != "WIN":

        return fail(
            "SAVED TRADE RESULT INVALID"
        )

    if not saved_trade.get("tp1_hit"):

        return fail(
            "SAVED TP1 STATE INVALID"
        )

    if not saved_trade.get("tp2_hit"):

        return fail(
            "SAVED TP2 STATE INVALID"
        )

    print()
    print(
        "RESULT: TRADE PERSISTENCE SUCCESS"
    )

    # =====================================================
    # 8. PERFORMANCE
    # =====================================================

    print()
    print("=" * 70)
    print("[8] PERFORMANCE")
    print("=" * 70)

    performance = get_performance()

    required_metrics = (
        "total_trades",
        "open_trades",
        "closed_trades",
        "wins",
        "losses",
        "win_rate",
        "total_percent",
        "total_r",
    )

    for metric in required_metrics:

        if metric not in performance:

            return fail(
                f"PERFORMANCE METRIC MISSING: {metric}"
            )

    print(
        f"Total Trades : "
        f"{performance['total_trades']}"
    )

    print(
        f"Open Trades  : "
        f"{performance['open_trades']}"
    )

    print(
        f"Closed Trades: "
        f"{performance['closed_trades']}"
    )

    print(
        f"Wins         : "
        f"{performance['wins']}"
    )

    print(
        f"Losses       : "
        f"{performance['losses']}"
    )

    print(
        f"Win Rate     : "
        f"{performance['win_rate']:.2f}%"
    )

    print(
        f"Total %      : "
        f"{performance['total_percent']:.2f}%"
    )

    print(
        f"Total R      : "
        f"{performance['total_r']:.2f}R"
    )

    # =====================================================
    # COMPLETE
    # =====================================================

    print()
    print("=" * 70)
    print(
        "ALL SIGNAL → TRADE TRACKER "
        "INTEGRATION TESTS PASSED"
    )
    print("=" * 70)

    return True


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    success = main()

    sys.exit(
        0 if success else 1
    )