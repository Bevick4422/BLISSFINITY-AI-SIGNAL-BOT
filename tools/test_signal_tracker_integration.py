"""
=========================================================
BLISSFINITY SIGNAL
Production Signal -> Trade Tracker Integration Test
=========================================================

Pipeline:

    Production Signal
        ↓
    Signal Validation
        ↓
    Signal Formatting
        ↓
    Trade Tracker
        ↓
    PENDING
        ↓
    ENTRY REACHED
        ↓
    OPEN
        ↓
    TP1
        ↓
    STOP MOVED TO ENTRY
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
from pathlib import Path

from signal_engine.signal_builder import (
    build_signal,
    validate_signal,
    format_signal,
)

from tracking import trade_tracker


# =========================================================
# TEST CONFIGURATION
# =========================================================

TEST_SYMBOL = "TEST/BTC"

TEST_TRADE_FILE = (
    Path(__file__).resolve().parents[1]
    / "tracking"
    / "test_trades.json"
)


# =========================================================
# FAILURE HELPER
# =========================================================

def fail(message: str) -> bool:

    print()
    print(f"RESULT: {message}")

    return False


# =========================================================
# CREATE TEST SIGNAL
# =========================================================

def create_signal() -> dict:

    return build_signal(
        symbol=TEST_SYMBOL,
        direction="BUY",
        setup="V Shape",
        entry=101.0,
        stop_loss=98.0,
        tp1=107.0,
        tp2=110.0,
        confidence=95.0,
        entry_type="LEFT_SHOULDER",
    )


# =========================================================
# DISPLAY SIGNAL
# =========================================================

def display_signal(signal: dict) -> None:

    print()
    print("SIGNAL")
    print("-" * 60)

    fields = (
        "symbol",
        "direction",
        "setup",
        "entry_type",
        "entry",
        "stop_loss",
        "risk",
        "tp1",
        "tp2",
        "rr",
        "confidence",
        "status",
        "valid",
    )

    for field in fields:

        print(
            f"{field:12}: "
            f"{signal.get(field)}"
        )


# =========================================================
# DISPLAY TRADE
# =========================================================

def display_trade(trade: dict) -> None:

    print()
    print("TRADE")
    print("-" * 60)

    fields = (
        "trade_id",
        "symbol",
        "direction",
        "setup",
        "entry",
        "stop_loss",
        "tp1",
        "tp2",
        "status",
        "state",
        "tp1_hit",
        "break_even",
        "result",
        "exit_price",
        "result_percent",
        "r_multiple",
    )

    for field in fields:

        print(
            f"{field:16}: "
            f"{trade.get(field)}"
        )


# =========================================================
# CLEAN TEST FILE
# =========================================================

def clean_test_file() -> None:

    if TEST_TRADE_FILE.exists():

        TEST_TRADE_FILE.unlink()


# =========================================================
# MAIN
# =========================================================

def main() -> bool:

    print()
    print("=" * 70)
    print(
        "BLISSFINITY SIGNAL | "
        "SIGNAL -> TRADE TRACKER INTEGRATION TEST"
    )
    print("=" * 70)

    original_trade_file = trade_tracker.TRADE_FILE

    trade_tracker.TRADE_FILE = TEST_TRADE_FILE

    clean_test_file()

    try:

        # =================================================
        # 1. PRODUCTION SIGNAL
        # =================================================

        print()
        print("=" * 70)
        print("[1] PRODUCTION SIGNAL")
        print("=" * 70)

        signal = create_signal()

        if not signal:

            return fail(
                "PRODUCTION SIGNAL CREATION FAILED"
            )

        display_signal(signal)

        if not validate_signal(signal):

            return fail(
                "SIGNAL VALIDATION FAILED"
            )

        print()
        print(
            "RESULT: PRODUCTION SIGNAL SUCCESS"
        )

        # =================================================
        # 2. SIGNAL FORMAT
        # =================================================

        print()
        print("=" * 70)
        print("[2] SIGNAL FORMAT")
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

        # =================================================
        # 3. RECORD SIGNAL
        # =================================================

        print()
        print("=" * 70)
        print("[3] RECORD SIGNAL")
        print("=" * 70)

        trade_id = trade_tracker.record_signal(
            signal
        )

        print(
            f"Trade ID: {trade_id}"
        )

        if not trade_id:

            return fail(
                "TRADE RECORD FAILED"
            )

        trades = trade_tracker.get_all_trades()

        if len(trades) != 1:

            return fail(
                "EXPECTED EXACTLY ONE TRADE"
            )

        trade = trades[0]

        display_trade(trade)

        if trade.get("status") != "PENDING":

            return fail(
                "NEW TRADE IS NOT PENDING"
            )

        if trade.get("state") != "PENDING":

            return fail(
                "NEW TRADE STATE IS NOT PENDING"
            )

        print()
        print(
            "RESULT: SIGNAL RECORDED AS PENDING"
        )

        # =================================================
        # 4. ENTRY REACHED
        # =================================================

        print()
        print("=" * 70)
        print("[4] ENTRY REACHED")
        print("=" * 70)

        trade = trade_tracker.update_trade(
            trade_id,
            current_price=101.0,
            candle_high=102.0,
            candle_low=100.0,
            candle_timestamp=1,
        )

        if trade is None:

            return fail(
                "ENTRY UPDATE FAILED"
            )

        display_trade(trade)

        if trade.get("status") != "OPEN":

            return fail(
                "TRADE DID NOT MOVE TO OPEN"
            )

        if trade.get("state") != "OPEN":

            return fail(
                "TRADE STATE DID NOT MOVE TO OPEN"
            )

        print()
        print(
            "RESULT: ENTRY REACHED - TRADE OPEN"
        )

        # =================================================
        # 5. TP1
        # =================================================

        print()
        print("=" * 70)
        print("[5] TP1")
        print("=" * 70)

        trade = trade_tracker.update_trade(
            trade_id,
            current_price=107.0,
            candle_high=108.0,
            candle_low=106.0,
            candle_timestamp=2,
        )

        if trade is None:

            return fail(
                "TP1 UPDATE FAILED"
            )

        display_trade(trade)

        if not trade.get("tp1_hit"):

            return fail(
                "TP1 WAS NOT REGISTERED"
            )

        if not trade.get("break_even"):

            return fail(
                "BREAK-EVEN WAS NOT ENABLED"
            )

        if float(trade.get("stop_loss")) != float(
            trade.get("entry")
        ):

            return fail(
                "STOP LOSS WAS NOT MOVED TO ENTRY"
            )

        if trade.get("status") != "OPEN":

            return fail(
                "TRADE CLOSED PREMATURELY AT TP1"
            )

        print()
        print(
            "RESULT: TP1 HIT - STOP MOVED TO ENTRY"
        )

        # =================================================
        # 6. TP2
        # =================================================

        print()
        print("=" * 70)
        print("[6] TP2")
        print("=" * 70)

        trade = trade_tracker.update_trade(
            trade_id,
            current_price=110.0,
            candle_high=111.0,
            candle_low=109.0,
            candle_timestamp=3,
        )

        if trade is None:

            return fail(
                "TP2 UPDATE FAILED"
            )

        display_trade(trade)

        if trade.get("status") != "WIN":

            return fail(
                "TP2 DID NOT CLOSE TRADE AS WIN"
            )

        if trade.get("result") != "WIN":

            return fail(
                "TP2 RESULT IS NOT WIN"
            )

        if float(trade.get("exit_price")) != float(
            signal["tp2"]
        ):

            return fail(
                "EXIT PRICE DOES NOT MATCH TP2"
            )

        print()
        print(
            "RESULT: TP2 HIT - TRADE CLOSED WIN"
        )

        # =================================================
        # 7. PERSISTENCE
        # =================================================

        print()
        print("=" * 70)
        print("[7] TRADE PERSISTENCE")
        print("=" * 70)

        saved_trades = trade_tracker.get_all_trades()

        if len(saved_trades) != 1:

            return fail(
                "PERSISTENCE TRADE COUNT INVALID"
            )

        saved_trade = saved_trades[0]

        display_trade(saved_trade)

        if saved_trade.get("trade_id") != trade_id:

            return fail(
                "PERSISTED TRADE ID INVALID"
            )

        if saved_trade.get("status") != "WIN":

            return fail(
                "PERSISTED TRADE STATUS INVALID"
            )

        if saved_trade.get("result") != "WIN":

            return fail(
                "PERSISTED TRADE RESULT INVALID"
            )

        if not saved_trade.get("tp1_hit"):

            return fail(
                "PERSISTED TP1 STATE INVALID"
            )

        if float(saved_trade.get("exit_price")) != float(
            signal["tp2"]
        ):

            return fail(
                "PERSISTED EXIT PRICE DOES NOT MATCH TP2"
            )

        print()
        print(
            "RESULT: TRADE PERSISTENCE SUCCESS"
        )

        # =================================================
        # 8. PERFORMANCE
        # =================================================

        print()
        print("=" * 70)
        print("[8] PERFORMANCE")
        print("=" * 70)

        performance = trade_tracker.get_performance()

        print(
            f"Total Trades : "
            f"{performance['total_trades']}"
        )

        print(
            f"Pending      : "
            f"{performance['pending_trades']}"
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
            f"Breakevens   : "
            f"{performance['breakevens']}"
        )

        print(
            f"Win Rate     : "
            f"{performance['win_rate']:.2f}%"
        )

        print(
            f"Net R        : "
            f"{performance['net_r']:.2f}R"
        )

        if performance["total_trades"] != 1:

            return fail(
                "PERFORMANCE TOTAL TRADES INVALID"
            )

        if performance["closed_trades"] != 1:

            return fail(
                "PERFORMANCE CLOSED TRADES INVALID"
            )

        if performance["wins"] != 1:

            return fail(
                "PERFORMANCE WIN COUNT INVALID"
            )

        if performance["losses"] != 0:

            return fail(
                "PERFORMANCE LOSS COUNT INVALID"
            )

        print()
        print(
            "RESULT: PERFORMANCE SUCCESS"
        )

        # =================================================
        # COMPLETE
        # =================================================

        print()
        print("=" * 70)
        print(
            "ALL SIGNAL -> TRADE TRACKER "
            "INTEGRATION TESTS PASSED"
        )
        print("=" * 70)

        return True

    finally:

        trade_tracker.TRADE_FILE = original_trade_file

        clean_test_file()


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    success = main()

    sys.exit(
        0 if success else 1
    )