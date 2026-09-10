"""
BLISSFINITY SIGNAL
Strategy -> Signal Builder -> Tracker Integration Test
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from engine.strategy_engine import evaluate_symbol
from engine.signal_builder import build_signal, validate_signal
import tracking.trade_tracker as trade_tracker


def create_daily_market_data() -> pd.DataFrame:
    """Create Daily candles with a valid bullish engulfing setup."""

    rows = []
    start_time = datetime.now(timezone.utc) - timedelta(days=250)

    price = 100.0

    for i in range(248):
        open_price = price
        close_price = price + 0.20

        rows.append(
            {
                "timestamp": start_time + timedelta(days=i),
                "open": open_price,
                "high": close_price + 1.00,
                "low": open_price - 1.00,
                "close": close_price,
                "volume": 1000.0,
            }
        )

        price = close_price

    rows.append(
        {
            "timestamp": start_time + timedelta(days=248),
            "open": 105.0,
            "high": 106.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1500.0,
        }
    )

    rows.append(
        {
            "timestamp": start_time + timedelta(days=249),
            "open": 99.0,
            "high": 110.0,
            "low": 98.0,
            "close": 108.0,
            "volume": 1800.0,
        }
    )

    return pd.DataFrame(rows)


def create_h4_market_data() -> pd.DataFrame:
    """Create H4 candles with a confirmed swing low at 90.0."""

    rows = []
    start_time = datetime.now(timezone.utc) - timedelta(hours=4 * 155)

    price = 100.0

    for i in range(145):
        open_price = price
        close_price = price + 0.30

        rows.append(
            {
                "timestamp": start_time + timedelta(hours=4 * i),
                "open": open_price,
                "high": close_price + 1.20,
                "low": open_price - 1.20,
                "close": close_price,
                "volume": 1000.0,
            }
        )

        price = close_price

    rows.append(
        {
            "timestamp": start_time + timedelta(hours=4 * 145),
            "open": 100.0,
            "high": 102.0,
            "low": 98.0,
            "close": 99.0,
            "volume": 1200.0,
        }
    )

    rows.append(
        {
            "timestamp": start_time + timedelta(hours=4 * 146),
            "open": 99.0,
            "high": 101.0,
            "low": 90.0,
            "close": 100.0,
            "volume": 1600.0,
        }
    )

    rows.append(
        {
            "timestamp": start_time + timedelta(hours=4 * 147),
            "open": 100.0,
            "high": 105.0,
            "low": 96.0,
            "close": 104.0,
            "volume": 1400.0,
        }
    )

    for i in range(148, 155):
        open_price = 104.0 + ((i - 148) * 0.50)
        close_price = open_price + 1.0

        rows.append(
            {
                "timestamp": start_time + timedelta(hours=4 * i),
                "open": open_price,
                "high": close_price + 2.0,
                "low": open_price - 1.0,
                "close": close_price,
                "volume": 1100.0,
            }
        )

    return pd.DataFrame(rows)


def display_signal(title: str, signal: dict) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    for key, value in signal.items():
        print(f"{key}: {value}")

    print("=" * 70)


def run_test() -> None:
    original_trade_file = trade_tracker.TRADE_FILE
    test_trade_file = Path(__file__).resolve().parents[1] / "tracking" / "test_trades.json"

    trade_tracker.TRADE_FILE = test_trade_file

    if test_trade_file.exists():
        test_trade_file.unlink()

    try:
        print()
        print("BLISSFINITY SIGNAL | STRATEGY -> SIGNAL -> TRACKER TEST")
        print(f"Test tracking file: {test_trade_file}")

        print()
        print("[1] MARKET DATA")

        daily = create_daily_market_data()
        h4 = create_h4_market_data()

        print(f"Daily candles    : {len(daily)}")
        print(f"H4 candles       : {len(h4)}")
        print(f"Daily last open  : {daily.iloc[-1]['open']}")
        print(f"Daily last close : {daily.iloc[-1]['close']}")
        print(f"H4 last close    : {h4.iloc[-1]['close']}")

        market_data = {
            "1d": daily,
            "4h": h4,
        }

        print("RESULT: MARKET DATA SUCCESS")

        print()
        print("[2] STRATEGY ENGINE")

        strategy_result = evaluate_symbol(
            symbol="TEST/BTC",
            market_data=market_data,
        )

        if not strategy_result:
            print("RESULT: STRATEGY PRODUCED NO TRADE")
            return

        display_signal("STRATEGY RESULT", strategy_result)
        print("RESULT: STRATEGY SUCCESS")

        print()
        print("[3] SIGNAL BUILDER")

        signal = build_signal(
            symbol=strategy_result["symbol"],
            direction=strategy_result["direction"],
            setup=strategy_result["setup"],
            candle_data=h4.iloc[-1].to_dict(),
            entry=float(strategy_result["entry"]),
            entry_type=strategy_result["entry_type"],
            market_data=h4,
            stop_loss=float(strategy_result["stop_loss"]),
            confidence=float(strategy_result.get("confidence", 80.0)),
        )

        if not signal:
            print("RESULT: SIGNAL BUILDER FAILED")
            return

        display_signal("PRODUCTION SIGNAL", signal)
        print("RESULT: SIGNAL BUILDER SUCCESS")

        print()
        print("[4] SIGNAL VALIDATION")

        validation_result = validate_signal(signal)
        print(f"Validation result: {validation_result}")

        if not validation_result:
            print("RESULT: SIGNAL VALIDATION FAILED")
            return

        print("RESULT: SIGNAL VALIDATION SUCCESS")

        print()
        print("[5] TRADE TRACKER")

        signal_id = signal.get("signal_id")

        tracked_trade = trade_tracker.record_signal(
            symbol=signal["symbol"],
            direction=signal["direction"],
            setup=signal["setup"],
            entry=float(signal["entry"]),
            stop_loss=float(signal["stop_loss"]),
            tp1=float(signal["tp1"]),
            tp2=float(signal["tp2"]),
            confidence=float(signal.get("confidence", 0.0)),
            signal_id=signal_id,
        )

        if not tracked_trade:
            print("RESULT: TRADE TRACKER FAILED")
            return

        print("Trade recorded successfully")
        print(f"Trade ID : {tracked_trade.get('trade_id')}")
        print(f"Signal ID: {tracked_trade.get('signal_id')}")
        print("RESULT: TRADE TRACKER SUCCESS")

        print()
        print("[6] TRADE RETRIEVAL")

        trade_id = tracked_trade.get("trade_id")
        retrieved_trade = trade_tracker.get_trade(trade_id)

        if not retrieved_trade:
            print("RESULT: TRADE RETRIEVAL FAILED")
            return

        print("Trade retrieved successfully")
        print(f"Retrieved trade ID: {retrieved_trade.get('trade_id')}")
        print(f"Retrieved status  : {retrieved_trade.get('status')}")
        print("RESULT: TRADE RETRIEVAL SUCCESS")

        print()
        print("[7] DUPLICATE PROTECTION")

        duplicate_trade = trade_tracker.record_signal(
            symbol=signal["symbol"],
            direction=signal["direction"],
            setup=signal["setup"],
            entry=float(signal["entry"]),
            stop_loss=float(signal["stop_loss"]),
            tp1=float(signal["tp1"]),
            tp2=float(signal["tp2"]),
            confidence=float(signal.get("confidence", 0.0)),
            signal_id=signal_id,
        )

        if duplicate_trade is not None and duplicate_trade.get("trade_id") == trade_id:
            print("Duplicate signal correctly rejected")
            print("Existing trade returned:", duplicate_trade.get("trade_id"))
            print("RESULT: DUPLICATE PROTECTION SUCCESS")
        else:
            print("RESULT: DUPLICATE PROTECTION FAILED")

        print()
        print("=" * 70)
        print("INTEGRATION TEST COMPLETED")
        print("=" * 70)

    finally:
        trade_tracker.TRADE_FILE = original_trade_file

        if test_trade_file.exists():
            test_trade_file.unlink()

        print()
        print("Test tracking file removed")
        print("Live tracking file preserved")


if __name__ == "__main__":
    run_test()