"""
BLISSFINITY SIGNAL
STEP 7 - Controlled Strategy Integration Tests
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import datetime, timedelta, timezone

import pandas as pd
from analysis.candle_gate import get_completed_candles
from analysis.risk.stoploss_engine import calculate_stop_loss
from engine.risk_engine import build_trade


def candles(rows):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    index = [
        start + timedelta(hours=4 * i)
        for i in range(len(rows))
    ]
    return pd.DataFrame(
        rows,
        index=pd.DatetimeIndex(index),
        columns=["open", "high", "low", "close", "volume"],
    )


def test_completed_candle_gate():
    df = candles([
        [100, 105, 95, 102, 1000],
        [102, 106, 99, 104, 1000],
    ])

    # Use a time after the first candle but before the second completes.
    now = df.index[1] + timedelta(hours=1)

    result = get_completed_candles(df, "4h", now=now)

    assert len(result) == 1
    assert float(result.iloc[-1]["close"]) == 102


def test_buy_structural_stop_and_risk():
    df = candles([
        [100, 105, 95, 102, 1000],
        [102, 110, 100, 108, 1000],
    ])

    stop = calculate_stop_loss(
        df=df,
        entry=108,
        direction="BUY",
        stop_reference={
            "type": "HL_WICK",
            "candle_index": 0,
        },
    )

    assert stop["valid"] is True
    assert stop["stop_loss"] == 95

    trade = build_trade(
        entry=108,
        stop_loss=95,
        direction="BUY",
        tp1_rr=2,
        tp2_rr=3,
    )

    assert trade["valid"] is True
    assert trade["risk"] == 13
    assert trade["tp1"] == 134
    assert trade["tp2"] == 147
    assert trade["rr"] == 3


def test_sell_structural_stop_and_risk():
    df = candles([
        [100, 115, 98, 110, 1000],
        [110, 112, 100, 103, 1000],
    ])

    stop = calculate_stop_loss(
        df=df,
        entry=103,
        direction="SELL",
        stop_reference={
            "type": "LH_WICK",
            "candle_index": 0,
        },
    )

    assert stop["valid"] is True
    assert stop["stop_loss"] == 115

    trade = build_trade(
        entry=103,
        stop_loss=115,
        direction="SELL",
        tp1_rr=2,
        tp2_rr=3,
    )

    assert trade["valid"] is True
    assert trade["risk"] == 12
    assert trade["tp1"] == 79
    assert trade["tp2"] == 67
    assert trade["rr"] == 3


def test_invalid_stop_is_rejected():
    df = candles([
        [100, 105, 95, 102, 1000],
    ])

    stop = calculate_stop_loss(
        df=df,
        entry=90,
        direction="BUY",
        stop_reference={
            "type": "HL_WICK",
            "candle_index": 0,
        },
    )

    assert stop["valid"] is False


def test_no_atr_fallback():
    df = candles([
        [100, 105, 95, 102, 1000],
    ])

    stop = calculate_stop_loss(
        df=df,
        entry=102,
        direction="BUY",
        stop_reference={},
    )

    assert stop["valid"] is False


if __name__ == "__main__":
    tests = [
        test_completed_candle_gate,
        test_buy_structural_stop_and_risk,
        test_sell_structural_stop_and_risk,
        test_invalid_stop_is_rejected,
        test_no_atr_fallback,
    ]

    passed = 0

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
        passed += 1

    print()
    print(f"{passed}/{len(tests)} CONTROLLED TESTS PASSED")
