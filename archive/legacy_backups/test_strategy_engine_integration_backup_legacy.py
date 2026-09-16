"""
BLISSFINITY SIGNAL
Controlled integration tests for engine.strategy_engine.evaluate_symbol.

These tests use synthetic CLOSED candles only.
No exchange/API/network calls are used.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import engine.strategy_engine as se


def make_df(rows, freq):
    idx = pd.date_range(
        "2026-01-01",
        periods=len(rows),
        freq=freq,
        tz="UTC",
    )

    return pd.DataFrame(
        rows,
        index=idx,
        columns=["open", "high", "low", "close", "volume"],
    )


def base_h4(n=16):
    rows = []
    price = 100.0

    for i in range(n):
        o = price
        c = price + (0.5 if i % 2 == 0 else -0.3)
        h = max(o, c) + 1.0
        l = min(o, c) - 1.0

        rows.append([o, h, l, c, 1000 + i])
        price = c

    return make_df(rows, "4h")


def bullish_daily_engulfing():
    """
    Valid bullish Daily structure:
    HH -> HL -> HH -> HL -> HH

    Final candle is a completed bullish body-only engulfing
    of the immediately preceding bearish candle.
    """
    rows = [
        [90, 95, 88, 94, 1000],    # 0
        [94, 100, 92, 99, 1000],   # 1 - swing high
        [99, 101, 96, 97, 1000],   # 2 - swing low
        [97, 105, 95, 104, 1000],  # 3 - higher high
        [104, 106, 99, 101, 1000], # 4 - higher low
        [101, 110, 100, 109, 1000],# 5 - higher high
        [109, 111, 104, 106, 1000],# 6 - higher low
        [106, 115, 105, 114, 1000],# 7 - higher high
        [114, 116, 109, 111, 1000],# 8 - higher low
        [111, 118, 110, 117, 1000],# 9 - higher high
        [117, 119, 108, 110, 1000],# 10 - bearish candle
        [109, 121, 107, 120, 1000],# 11 - bullish engulfing
    ]

    return make_df(rows, "1d")


def bearish_daily_engulfing():
    """
    Valid bearish Daily structure:
    LL -> LH -> LL -> LH -> LL

    Final candle is a completed bearish body-only engulfing
    of the immediately preceding bullish candle.
    """
    rows = [
        [120, 122, 115, 118, 1000],# 0
        [118, 121, 112, 114, 1000],# 1 - swing low
        [114, 116, 109, 113, 1000],# 2 - lower high
        [113, 115, 105, 107, 1000],# 3 - lower low
        [107, 110, 103, 106, 1000],# 4 - lower high
        [106, 108, 98, 100, 1000], # 5 - lower low
        [100, 103, 96, 99, 1000],  # 6 - lower high
        [99, 101, 92, 94, 1000],   # 7 - lower low
        [94, 97, 90, 92, 1000],    # 8 - lower high
        [92, 95, 86, 88, 1000],    # 9 - lower low
        [88, 96, 85, 95, 1000],    # 10 - bullish candle
        [96, 97, 82, 84, 1000],    # 11 - bearish engulfing
    ]

    return make_df(rows, "1d")

def ranging_daily():
    rows = [
        [100, 103, 97, 101, 1000],
        [101, 104, 98, 100, 1000],
        [100, 103, 97, 102, 1000],
        [102, 105, 99, 101, 1000],
        [101, 104, 98, 100, 1000],
        [100, 103, 97, 101, 1000],
        [101, 104, 98, 100, 1000],
        [100, 103, 97, 101, 1000],
    ]

    return make_df(rows, "1d")


def valid_market(daily):
    return {
        "1d": daily,
        "4h": base_h4(),
    }


def structural_daily_stub(direction="BUY", setup="V_SHAPE"):
    return {
        "valid": True,
        "trend": "BULLISH" if direction == "BUY" else "BEARISH",
        "structure": ["HH", "HL", "HH", "HL"],
        "setup": setup,
        "direction": direction,
        "level": 100.0,
        "level_index": 5,
        "setup_candle_index": 5,
        "entry": None,
    }


def valid_bos(direction="BUY"):
    return {
        "bos": True,
        "direction": direction,
        "key_level": 100.0,
        "broken_level": 100.0,
        "key_level_index": 5,
        "break_index": 10,
        "reason": "controlled test BOS",
    }


def valid_retest():
    return {
        "valid": True,
        "entry": 100.0,
        "retest_index": 12,
        "confidence": 85.0,
        "stop_reference": {
            "type": "KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 5,
        },
    }


def valid_stop():
    return {
        "valid": True,
        "stop_loss": 95.0,
        "reason": "controlled structural stop",
        "stop_reference": {
            "type": "KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 5,
        },
    }


def valid_trade():
    return {
        "valid": True,
        "entry": 100.0,
        "stop_loss": 95.0,
        "risk": 5.0,
        "tp1": 110.0,
        "tp2": 115.0,
        "rr": 3.0,
    }


def valid_signal():
    return {
        "valid": True,
        "symbol": "TESTUSDT",
        "direction": "BUY",
        "setup": "V_SHAPE",
        "entry_type": "BREAK_RETEST",
        "entry": 100.0,
        "stop_loss": 95.0,
        "risk": 5.0,
        "tp1": 110.0,
        "tp2": 115.0,
        "rr": 3.0,
        "confidence": 85.0,
    }


def test_daily_bullish_engulfing_direct():
    daily = bullish_daily_engulfing()

    result = se.evaluate_symbol(
        "TESTUSDT",
        valid_market(daily),
    )

    assert result is not None, (
        "Bullish Daily Engulfing should produce a signal"
    )

    assert result["direction"] == "BUY"
    assert result["entry_type"] == "ENGULFING"

    return "PASS: test_daily_bullish_engulfing_direct"


def test_daily_bearish_engulfing_direct():
    daily = bearish_daily_engulfing()

    result = se.evaluate_symbol(
        "TESTUSDT",
        valid_market(daily),
    )

    assert result is not None, (
        "Bearish Daily Engulfing should produce a signal"
    )

    assert result["direction"] == "SELL"
    assert result["entry_type"] == "ENGULFING"

    return "PASS: test_daily_bearish_engulfing_direct"


def test_range_no_signal():
    daily = ranging_daily()

    result = se.evaluate_symbol(
        "TESTUSDT",
        valid_market(daily),
    )

    assert result is None, "Range must produce no signal"

    return "PASS: test_range_no_signal"


def test_structural_no_bos_no_signal():
    original = se.detect_daily_setup

    try:
        se.detect_daily_setup = (
            lambda df: structural_daily_stub("BUY")
        )

        result = se.evaluate_symbol(
            "TESTUSDT",
            valid_market(bullish_daily_engulfing()),
        )

        assert result is None, (
            "No H4 BOS must produce no signal"
        )

    finally:
        se.detect_daily_setup = original

    return "PASS: test_structural_no_bos_no_signal"


def test_structural_bos_no_retest_no_signal():
    original_daily = se.detect_daily_setup
    original_bos = se.detect_h4_bos
    original_retest = se.detect_break_retest

    try:
        se.detect_daily_setup = (
            lambda df: structural_daily_stub("BUY")
        )

        se.detect_h4_bos = (
            lambda df: valid_bos("BUY")
        )

        se.detect_break_retest = (
            lambda **kwargs: {
                "valid": False,
                "reason": "Required retest has not occurred",
            }
        )

        result = se.evaluate_symbol(
            "TESTUSDT",
            valid_market(bullish_daily_engulfing()),
        )

        assert result is None, (
            "BOS without retest must produce no signal"
        )

    finally:
        se.detect_daily_setup = original_daily
        se.detect_h4_bos = original_bos
        se.detect_break_retest = original_retest

    return "PASS: test_structural_bos_no_retest_no_signal"


def test_structural_valid_bos_and_retest_signal():
    original_daily = se.detect_daily_setup
    original_bos = se.detect_h4_bos
    original_retest = se.detect_break_retest
    original_stop = se.calculate_stop_loss
    original_trade = se.build_trade
    original_signal = se.build_production_signal
    original_validate = se.validate_signal

    try:
        se.detect_daily_setup = (
            lambda df: structural_daily_stub("BUY")
        )

        se.detect_h4_bos = (
            lambda df: valid_bos("BUY")
        )

        se.detect_break_retest = (
            lambda **kwargs: valid_retest()
        )

        se.calculate_stop_loss = (
            lambda **kwargs: valid_stop()
        )

        se.build_trade = (
            lambda **kwargs: valid_trade()
        )

        se.build_production_signal = (
            lambda **kwargs: valid_signal()
        )

        se.validate_signal = (
            lambda signal: True
        )

        result = se.evaluate_symbol(
            "TESTUSDT",
            valid_market(bullish_daily_engulfing()),
        )

        assert result is not None, (
            "Valid BOS + retest should produce a signal"
        )

        assert result["entry_type"] == "BREAK_RETEST"
        assert result["direction"] == "BUY"

    finally:
        se.detect_daily_setup = original_daily
        se.detect_h4_bos = original_bos
        se.detect_break_retest = original_retest
        se.calculate_stop_loss = original_stop
        se.build_trade = original_trade
        se.build_production_signal = original_signal
        se.validate_signal = original_validate

    return "PASS: test_structural_valid_bos_and_retest_signal"


def test_structural_wrong_bos_direction_no_signal():
    original_daily = se.detect_daily_setup
    original_bos = se.detect_h4_bos

    try:
        se.detect_daily_setup = (
            lambda df: structural_daily_stub("BUY")
        )

        se.detect_h4_bos = (
            lambda df: valid_bos("SELL")
        )

        result = se.evaluate_symbol(
            "TESTUSDT",
            valid_market(bullish_daily_engulfing()),
        )

        assert result is None, (
            "Opposite H4 BOS direction must produce no signal"
        )

    finally:
        se.detect_daily_setup = original_daily
        se.detect_h4_bos = original_bos

    return "PASS: test_structural_wrong_bos_direction_no_signal"


def test_forming_candles_ignored():
    daily = bullish_daily_engulfing().copy()
    h4 = base_h4().copy()

    now = pd.Timestamp.now(tz="UTC")

    daily.index = pd.date_range(
        now - pd.Timedelta(days=len(daily) - 1),
        periods=len(daily),
        freq="1D",
        tz="UTC",
    )

    h4.index = pd.date_range(
        now - pd.Timedelta(hours=4 * (len(h4) - 1)),
        periods=len(h4),
        freq="4h",
        tz="UTC",
    )

    daily.iloc[
        -1,
        daily.columns.get_loc("close")
    ] = 999.0

    h4.iloc[
        -1,
        h4.columns.get_loc("close")
    ] = 999.0

    result = se.evaluate_symbol(
        "TESTUSDT",
        {
            "1d": daily,
            "4h": h4,
        },
    )

    assert (
        result is None
        or result.get("entry") != 999.0
    ), "Forming candle data must not be used"

    return "PASS: test_forming_candles_ignored"


def test_invalid_structural_stop_no_signal():
    original_daily = se.detect_daily_setup
    original_bos = se.detect_h4_bos
    original_retest = se.detect_break_retest
    original_stop = se.calculate_stop_loss

    try:
        se.detect_daily_setup = (
            lambda df: structural_daily_stub("BUY")
        )

        se.detect_h4_bos = (
            lambda df: valid_bos("BUY")
        )

        se.detect_break_retest = (
            lambda **kwargs: valid_retest()
        )

        se.calculate_stop_loss = (
            lambda **kwargs: {
                "valid": False,
                "reason": "BUY stop must be below entry",
            }
        )

        result = se.evaluate_symbol(
            "TESTUSDT",
            valid_market(bullish_daily_engulfing()),
        )

        assert result is None, (
            "Invalid structural SL must produce no signal"
        )

    finally:
        se.detect_daily_setup = original_daily
        se.detect_h4_bos = original_bos
        se.detect_break_retest = original_retest
        se.calculate_stop_loss = original_stop

    return "PASS: test_invalid_structural_stop_no_signal"


def main():
    tests = [
        test_daily_bullish_engulfing_direct,
        test_daily_bearish_engulfing_direct,
        test_range_no_signal,
        test_structural_no_bos_no_signal,
        test_structural_bos_no_retest_no_signal,
        test_structural_valid_bos_and_retest_signal,
        test_structural_wrong_bos_direction_no_signal,
        test_forming_candles_ignored,
        test_invalid_structural_stop_no_signal,
    ]

    passed = 0

    for test in tests:
        try:
            print(test())
            passed += 1

        except Exception as exc:
            print(
                f"FAIL: {test.__name__}: "
                f"{type(exc).__name__}: {exc}"
            )

    print()
    print(
        f"{passed}/{len(tests)} "
        "STRATEGY ENGINE INTEGRATION TESTS PASSED"
    )

    raise SystemExit(
        0 if passed == len(tests) else 1
    )


if __name__ == "__main__":
    main()