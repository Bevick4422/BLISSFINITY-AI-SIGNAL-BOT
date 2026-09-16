"""
=====================================================
BLISSFINITY SIGNAL
Strategy -> Signal -> Tracker Integration Test
Production Architecture
=====================================================
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from engine.strategy_engine import evaluate_symbol
from signal_engine.signal_builder import validate_signal
import tracking.trade_tracker as trade_tracker


# =====================================================
# TEST TRACKING FILE
# =====================================================

TEST_TRADE_FILE = (
    Path(__file__).resolve().parents[1]
    / "tracking"
    / "test_trades.json"
)


# =====================================================
# TEST MARKET DATA
# =====================================================

def build_daily_data() -> pd.DataFrame:
    """
    Build deterministic Daily candles containing a
    valid bullish engulfing setup.
    """

    rows = []

    for i in range(249):
        rows.append(
            {
                "timestamp": i,
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1000.0,
            }
        )

    # Previous bearish candle
    rows.append(
        {
            "timestamp": 249,
            "open": 105.0,
            "high": 106.0,
            "low": 98.0,
            "close": 100.0,
            "volume": 1000.0,
        }
    )

    # Current bullish engulfing candle
    rows.append(
        {
            "timestamp": 250,
            "open": 99.0,
            "high": 110.0,
            "low": 98.0,
            "close": 108.0,
            "volume": 1000.0,
        }
    )

    return pd.DataFrame(rows)


def build_h4_data() -> pd.DataFrame:
    """
    Build deterministic H4 candles.

    H4 BOS is not required for a Daily Engulfing setup,
    but sufficient H4 data is supplied for the production
    Strategy Engine.
    """

    rows = []

    for i in range(154):
        rows.append(
            {
                "timestamp": i,
                "open": 100.0,
                "high": 101.0,
                "low": 90.0,
                "close": 100.0,
                "volume": 1000.0,
            }
        )

    rows.append(
        {
            "timestamp": 154,
            "open": 100.0,
            "high": 109.0,
            "low": 99.0,
            "close": 108.0,
            "volume": 1000.0,
        }
    )

    return pd.DataFrame(rows)


# =====================================================
# CLEAN TEST FILE
# =====================================================

def remove_test_file() -> None:
    """
    Remove the isolated test tracking file.
    """

    try:
        if TEST_TRADE_FILE.exists():
            TEST_TRADE_FILE.unlink()
    except OSError:
        pass


# =====================================================
# MAIN TEST
# =====================================================

def run_test() -> None:

    print(
        "\nBLISSFINITY SIGNAL | "
        "STRATEGY -> SIGNAL -> TRACKER TEST"
    )

    print(
        f"Test tracking file: {TEST_TRADE_FILE}"
    )

    # -------------------------------------------------
    # Redirect tracker storage to isolated test file.
    # -------------------------------------------------

    original_trade_file = trade_tracker.TRADE_FILE
    trade_tracker.TRADE_FILE = TEST_TRADE_FILE

    remove_test_file()

    try:

        # =================================================
        # 1. MARKET DATA
        # =================================================

        daily = build_daily_data()
        h4 = build_h4_data()

        market_data = {
            "1d": daily,
            "4h": h4,
        }

        print("\n[1] MARKET DATA")

        print(
            f"Daily candles    : {len(daily)}"
        )

        print(
            f"H4 candles       : {len(h4)}"
        )

        print(
            f"Daily last open  : "
            f"{daily.iloc[-1]['open']}"
        )

        print(
            f"Daily last close : "
            f"{daily.iloc[-1]['close']}"
        )

        print(
            f"H4 last close    : "
            f"{h4.iloc[-1]['close']}"
        )

        print("RESULT: MARKET DATA SUCCESS")

        # =================================================
        # 2. STRATEGY ENGINE
        # =================================================

        print("\n[2] STRATEGY ENGINE")

        signal = evaluate_symbol(
            "TEST/BTC",
            market_data,
        )

        if not signal:
            raise AssertionError(
                "Strategy Engine returned no signal."
            )

        print(
            "\n"
            + "=" * 70
        )
        print("PRODUCTION SIGNAL")
        print("=" * 70)

        for key, value in signal.items():
            print(
                f"{key}: {value}"
            )

        print("=" * 70)

        if signal.get("production_signal") is not True:
            raise AssertionError(
                "Strategy Engine did not return "
                "a production signal."
            )

        print(
            "RESULT: STRATEGY SUCCESS"
        )

        # =================================================
        # 3. PRODUCTION SIGNAL VALIDATION
        # =================================================

        print(
            "\n[3] PRODUCTION SIGNAL VALIDATION"
        )

        valid = validate_signal(
            signal
        )

        print(
            f"Validation result: {valid}"
        )

        if valid is not True:
            raise AssertionError(
                "Production signal failed validation."
            )

        print(
            "RESULT: SIGNAL VALIDATION SUCCESS"
        )

        # =================================================
        # 4. TRADE TRACKER
        # =================================================

        print(
            "\n[4] TRADE TRACKER"
        )

        trade_id = (
            trade_tracker.record_signal(
                signal
            )
        )

        print(
            f"Trade ID: {trade_id}"
        )

        if not trade_id:
            raise AssertionError(
                "Trade Tracker did not record the signal."
            )

        # -------------------------------------------------
        # Verify stored trade.
        # -------------------------------------------------

        trades = (
            trade_tracker.get_all_trades()
        )

        if len(trades) != 1:
            raise AssertionError(
                f"Expected 1 tracked trade, "
                f"found {len(trades)}."
            )

        trade = trades[0]

        print(
            "\nStored trade:"
        )

        print(
            json.dumps(
                trade,
                indent=2,
                ensure_ascii=False,
            )
        )

        # -------------------------------------------------
        # Verify identity.
        # -------------------------------------------------

        if trade.get("trade_id") != trade_id:
            raise AssertionError(
                "Stored trade ID does not match "
                "returned trade ID."
            )

        if trade.get("symbol") != signal["symbol"]:
            raise AssertionError(
                "Tracked symbol does not match signal."
            )

        if trade.get("direction") != signal["direction"]:
            raise AssertionError(
                "Tracked direction does not match signal."
            )

        if trade.get("setup") != signal["setup"]:
            raise AssertionError(
                "Tracked setup does not match signal."
            )

        # -------------------------------------------------
        # Verify trade values.
        # -------------------------------------------------

        fields = [
            "entry",
            "stop_loss",
            "tp1",
            "tp2",
            "risk",
            "rr",
            "confidence",
        ]

        for field in fields:

            if trade.get(field) != signal.get(field):

                raise AssertionError(
                    f"Tracked {field} does not "
                    f"match production signal."
                )

        # -------------------------------------------------
        # New trades must begin PENDING.
        # -------------------------------------------------

        if trade.get("status") != "PENDING":
            raise AssertionError(
                "New tracked trade is not PENDING."
            )

        if trade.get("state") != "PENDING":
            raise AssertionError(
                "New tracked trade state is not PENDING."
            )

        print(
            "\nRESULT: TRADE RECORDING SUCCESS"
        )

        # =================================================
        # 5. DUPLICATE PROTECTION
        # =================================================

        print(
            "\n[5] DUPLICATE PROTECTION"
        )

        duplicate_trade_id = (
            trade_tracker.record_signal(
                signal
            )
        )

        print(
            f"Original trade ID : {trade_id}"
        )

        print(
            f"Second record ID  : {duplicate_trade_id}"
        )

        if duplicate_trade_id != trade_id:
            raise AssertionError(
                "Duplicate protection failed."
            )

        trades_after_duplicate = (
            trade_tracker.get_all_trades()
        )

        if len(trades_after_duplicate) != 1:
            raise AssertionError(
                "Duplicate signal created "
                "another trade."
            )

        print(
            "RESULT: DUPLICATE PROTECTION SUCCESS"
        )

        # =================================================
        # FINAL RESULT
        # =================================================

        print(
            "\n"
            + "=" * 70
        )

        print(
            "STRATEGY -> SIGNAL -> TRACKER"
        )

        print(
            "INTEGRATION TEST PASSED"
        )

        print("=" * 70)

    finally:

        # Restore production tracker path.
        trade_tracker.TRADE_FILE = (
            original_trade_file
        )

        remove_test_file()

        print(
            "\nTest tracking file removed"
        )

        print(
            "Live tracking file preserved"
        )


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_test()