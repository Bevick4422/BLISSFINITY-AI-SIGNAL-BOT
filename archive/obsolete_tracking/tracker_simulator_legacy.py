"""
=====================================================
BLISSFINITY SIGNAL
Safe Trade Tracker Simulator
=====================================================

Tests:
1. TP2 WIN
2. Stop-loss LOSS
3. Break-even after TP1

The simulator uses a temporary trades.json file.
It does not modify real trading records.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import trade_tracker as tracker


def print_trade(label: str, trade: dict | None) -> None:
    """Print the important fields of a trade."""

    print(f"\n--- {label} ---")

    if trade is None:
        print("Trade not found")
        return

    print(
        json.dumps(
            {
                "trade_id": trade.get("trade_id"),
                "symbol": trade.get("symbol"),
                "direction": trade.get("direction"),
                "status": trade.get("status"),
                "state": trade.get("state"),
                "result": trade.get("result"),
                "entry": trade.get("entry"),
                "stop_loss": trade.get("stop_loss"),
                "original_risk": trade.get("original_risk"),
                "tp1": trade.get("tp1"),
                "tp2": trade.get("tp2"),
                "tp1_hit": trade.get("tp1_hit"),
                "break_even": trade.get("break_even"),
                "exit_price": trade.get("exit_price"),
                "result_percent": trade.get("result_percent"),
                "r_multiple": trade.get("r_multiple"),
            },
            indent=2,
        )
    )


def create_signal(
    symbol: str,
    direction: str = "BUY",
) -> dict:
    """Create a standard test signal."""

    return {
        "symbol": symbol,
        "direction": direction,
        "setup": "Simulator Test",
        "entry": 100.0,
        "stop_loss": 90.0,
        "tp1": 120.0,
        "tp2": 130.0,
        "risk": 10.0,
        "rr": 3.0,
        "confidence": 90.0,
    }


def run_win_test() -> bool:
    """Test entry, TP1, break-even, and TP2 win."""

    print("\n\n==============================")
    print("TEST 1: TP2 WIN")
    print("==============================")

    trade_id = tracker.record_signal(
        create_signal("WIN/USDT")
    )

    if not trade_id:
        print("FAIL: Could not create win trade.")
        return False

    trade = tracker.update_trade(trade_id, 100.0)
    print_trade("Entry Reached", trade)

    trade = tracker.update_trade(trade_id, 120.0)
    print_trade("TP1 Reached", trade)

    trade = tracker.update_trade(trade_id, 130.0)
    print_trade("TP2 Reached", trade)

    passed = (
        trade is not None
        and trade.get("status") == "WIN"
        and trade.get("state") == "WIN"
        and trade.get("result") == "WIN"
        and trade.get("tp1_hit") is True
        and trade.get("break_even") is True
        and trade.get("exit_price") == 130.0
        and trade.get("original_risk") == 10.0
        and trade.get("r_multiple") == 3.0
    )

    if passed:
        print("\nPASS: TP2 win lifecycle works.")
    else:
        print("\nFAIL: TP2 win lifecycle failed.")

    return passed


def run_loss_test() -> bool:
    """Test entry followed by stop-loss."""

    print("\n\n==============================")
    print("TEST 2: STOP-LOSS LOSS")
    print("==============================")

    trade_id = tracker.record_signal(
        create_signal("LOSS/USDT")
    )

    if not trade_id:
        print("FAIL: Could not create loss trade.")
        return False

    trade = tracker.update_trade(trade_id, 100.0)
    print_trade("Entry Reached", trade)

    trade = tracker.update_trade(trade_id, 90.0)
    print_trade("Stop Loss Reached", trade)

    passed = (
        trade is not None
        and trade.get("status") == "LOSS"
        and trade.get("state") == "LOSS"
        and trade.get("result") == "LOSS"
        and trade.get("exit_price") == 90.0
        and trade.get("original_risk") == 10.0
        and trade.get("r_multiple") == -1.0
    )

    if passed:
        print("\nPASS: Stop-loss lifecycle works.")
    else:
        print("\nFAIL: Stop-loss lifecycle failed.")

    return passed


def run_breakeven_test() -> bool:
    """Test TP1 followed by a break-even exit."""

    print("\n\n==============================")
    print("TEST 3: BREAK-EVEN")
    print("==============================")

    trade_id = tracker.record_signal(
        create_signal("BREAKEVEN/USDT")
    )

    if not trade_id:
        print("FAIL: Could not create break-even trade.")
        return False

    trade = tracker.update_trade(trade_id, 100.0)
    print_trade("Entry Reached", trade)

    trade = tracker.update_trade(trade_id, 120.0)
    print_trade("TP1 Reached", trade)

    trade = tracker.update_trade(trade_id, 100.0)
    print_trade("Break-Even Reached", trade)

    passed = (
        trade is not None
        and trade.get("status") == "BREAKEVEN"
        and trade.get("state") == "BREAKEVEN"
        and trade.get("result") == "BREAKEVEN"
        and trade.get("exit_price") == 100.0
        and trade.get("original_risk") == 10.0
        and trade.get("r_multiple") == 0.0
    )

    if passed:
        print("\nPASS: Break-even lifecycle works.")
    else:
        print("\nFAIL: Break-even lifecycle failed.")

    return passed


def main() -> None:
    """Run all tests using a temporary trade file."""

    original_trade_file = tracker.TRADE_FILE

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker.TRADE_FILE = (
                Path(temp_dir) / "test_trades.json"
            )

            win_passed = run_win_test()
            loss_passed = run_loss_test()
            breakeven_passed = run_breakeven_test()

            summary = tracker.get_performance()

            print("\n\n==============================")
            print("FINAL SIMULATION SUMMARY")
            print("==============================")
            print(json.dumps(summary, indent=2))

            expected = {
                "total_trades": 3,
                "pending_trades": 0,
                "open_trades": 0,
                "wins": 1,
                "losses": 1,
                "breakevens": 1,
                "closed_trades": 3,
                "active_trades": 0,
                "net_r": 2.0,
                "win_rate": 33.33,
            }

            summary_matches = (
                summary.get("total_trades") == expected["total_trades"]
                and summary.get("pending_trades") == expected["pending_trades"]
                and summary.get("open_trades") == expected["open_trades"]
                and summary.get("wins") == expected["wins"]
                and summary.get("losses") == expected["losses"]
                and summary.get("breakevens") == expected["breakevens"]
                and summary.get("closed_trades") == expected["closed_trades"]
                and summary.get("active_trades") == expected["active_trades"]
                and summary.get("net_r") == expected["net_r"]
                and round(summary.get("win_rate", 0.0), 2) == expected["win_rate"]
            )

            print("\n==============================")

            if (
                win_passed
                and loss_passed
                and breakeven_passed
                and summary_matches
            ):
                print("PASS: All trade lifecycle tests passed.")
            else:
                print("FAIL: One or more simulator tests failed.")

            print("==============================")

    finally:
        tracker.TRADE_FILE = original_trade_file


if __name__ == "__main__":
    main()