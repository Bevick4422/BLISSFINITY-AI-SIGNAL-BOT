"""
BLISSFINITY SIGNAL
STEP 6 - Risk + Production Signal Assembly Test

Tests the actual installed engine.risk_engine and
signal_engine.signal_builder modules.

No exchange, Telegram, tracker, or main.py is used.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.risk_engine import build_trade
from signal_engine.signal_builder import build_signal, validate_signal


def test_buy_assembly():
    trade = build_trade(
        entry=100.0,
        stop_loss=95.0,
        direction="BUY",
        tp1_rr=2.0,
        tp2_rr=3.0,
    )

    assert trade["valid"] is True
    assert trade["risk"] == 5.0
    assert trade["tp1"] == 110.0
    assert trade["tp2"] == 115.0
    assert trade["rr"] == 3.0

    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction="BUY",
        setup="Bullish Engulfing",
        entry=trade["entry"],
        stop_loss=trade["stop_loss"],
        tp1=trade["tp1"],
        tp2=trade["tp2"],
        confidence=90.0,
        entry_type="ENGULFING",
    )

    assert signal is not None
    assert signal["valid"] is True
    assert signal["direction"] == "BUY"
    assert signal["entry"] == 100.0
    assert signal["stop_loss"] == 95.0
    assert signal["tp1"] == 110.0
    assert signal["tp2"] == 115.0
    assert validate_signal(signal) is True


def test_sell_assembly():
    trade = build_trade(
        entry=100.0,
        stop_loss=105.0,
        direction="SELL",
        tp1_rr=2.0,
        tp2_rr=3.0,
    )

    assert trade["valid"] is True
    assert trade["risk"] == 5.0
    assert trade["tp1"] == 90.0
    assert trade["tp2"] == 85.0
    assert trade["rr"] == 3.0

    signal = build_signal(
        symbol="ETH/USDT:USDT",
        direction="SELL",
        setup="Bearish Engulfing",
        entry=trade["entry"],
        stop_loss=trade["stop_loss"],
        tp1=trade["tp1"],
        tp2=trade["tp2"],
        confidence=90.0,
        entry_type="ENGULFING",
    )

    assert signal is not None
    assert signal["valid"] is True
    assert signal["direction"] == "SELL"
    assert signal["entry"] == 100.0
    assert signal["stop_loss"] == 105.0
    assert signal["tp1"] == 90.0
    assert signal["tp2"] == 85.0
    assert validate_signal(signal) is True


def test_invalid_buy_signal_rejected():
    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction="BUY",
        setup="Bullish Engulfing",
        entry=100.0,
        stop_loss=105.0,
        tp1=110.0,
        tp2=115.0,
        confidence=90.0,
        entry_type="ENGULFING",
    )

    assert signal is None or validate_signal(signal) is False


def test_invalid_sell_signal_rejected():
    signal = build_signal(
        symbol="ETH/USDT:USDT",
        direction="SELL",
        setup="Bearish Engulfing",
        entry=100.0,
        stop_loss=95.0,
        tp1=90.0,
        tp2=85.0,
        confidence=90.0,
        entry_type="ENGULFING",
    )

    assert signal is None or validate_signal(signal) is False


if __name__ == "__main__":
    tests = [
        test_buy_assembly,
        test_sell_assembly,
        test_invalid_buy_signal_rejected,
        test_invalid_sell_signal_rejected,
    ]

    passed = 0

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
        passed += 1

    print()
    print(f"{passed}/{len(tests)} RISK + SIGNAL ASSEMBLY TESTS PASSED")
