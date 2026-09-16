"""
BLISSFINITY SIGNAL
Clean integration tests for engine.strategy_engine.evaluate_symbol.

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


# ============================================================
# DATA HELPERS
# ============================================================

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
        c = price + 0.5 if i % 2 == 0 else price - 0.3

        h = max(o, c) + 1.0
        l = min(o, c) - 1.0

        rows.append([o, h, l, c, 1000 + i])
        price = c

    return make_df(rows, "4h")


def valid_market(daily):
    return {
        "1d": daily,
        "4h": base_h4(),
    }


# ============================================================
# DAILY ENGULFING FIXTURES
# ============================================================

def bullish_daily_engulfing():
    """
    Final completed candle is a bullish body-only engulfing
    of the immediately preceding bearish candle.
    """

    rows = [
        [90, 95, 88, 94, 1000],
        [94, 100, 92, 99, 1000],
        [99, 101, 96, 97, 1000],
        [97, 105, 95, 104, 1000],
        [104, 106, 99, 101, 1000],
        [101, 110, 100, 109, 1000],
        [109, 111, 104, 106, 1000],
        [106, 115, 105, 114, 1000],
        [114, 116, 109, 111, 1000],
        [111, 118, 110, 117, 1000],
        [117, 119, 108, 110, 1000],
        [109, 121, 107, 120, 1000],
    ]

    return make_df(rows, "D")


def bearish_daily_engulfing():
    """
    Final completed candle is a bearish body-only engulfing
    of the immediately preceding bullish candle.
    """

    rows = [
        [120, 122, 115, 118, 1000],
        [118, 121, 112, 114, 1000],
        [114, 116, 109, 113, 1000],
        [113, 115, 105, 107, 1000],
        [107, 110, 103, 106, 1000],
        [106, 108, 98, 100, 1000],
        [100, 103, 96, 99, 1000],
        [99, 101, 92, 94, 1000],
        [94, 97, 90, 92, 1000],
        [92, 95, 86, 88, 1000],
        [88, 96, 85, 95, 1000],
        [96, 97, 82, 84, 1000],
    ]

    return make_df(rows, "D")


# ============================================================
# RANGE FIXTURE
# ============================================================

def ranging_daily():
    """
    Genuine Daily range.

    The candles deliberately use equal open/close (doji) bodies
    so the fixture cannot accidentally create a body engulfing
    pattern. Price remains inside a narrow horizontal area.
    """

    rows = [
        [100.0, 102.0, 98.0, 100.0, 1000],
        [101.0, 103.0, 99.0, 101.0, 1000],
        [100.5, 102.5, 98.5, 100.5, 1000],
        [101.5, 103.0, 99.0, 101.5, 1000],
        [100.0, 102.5, 98.0, 100.0, 1000],
        [101.0, 103.0, 99.0, 101.0, 1000],
        [100.5, 102.5, 98.5, 100.5, 1000],
        [101.0, 103.0, 99.0, 101.0, 1000],
    ]

    return make_df(rows, "D")


# ============================================================
# STRUCTURAL FIXTURES
# ============================================================

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


def invalid_stop():
    return {
        "valid": True,
        "stop_loss": 105.0,
        "reason": "intentionally invalid BUY stop",
        "stop_reference": {
            "type": "KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 5,
        },
    }


# ============================================================
# MOCK PIPELINE
# ============================================================

def patch_pipeline(
    monkeypatch,
    *,
    bos_result=None,
    retest_result=None,
    stop_result=None,
):
    """
    Patch only downstream structural components.

    Mock functions intentionally accept *args and **kwargs so they
    remain compatible with production keyword arguments.
    """

    if bos_result is not None:

        def fake_bos(*args, **kwargs):
            return bos_result

        monkeypatch.setattr(se, "detect_h4_bos", fake_bos)

    if retest_result is not None:

        def fake_retest(*args, **kwargs):
            return retest_result

        monkeypatch.setattr(se, "detect_break_retest", fake_retest)

    if stop_result is not None:

        def fake_stop(*args, **kwargs):
            return stop_result

        monkeypatch.setattr(se, "calculate_stop_loss", fake_stop)


# ============================================================
# TEST 1 — DAILY BULLISH ENGULFING
# ============================================================

def test_daily_bullish_engulfing_direct(monkeypatch):
    """
    Bullish Daily Engulfing:

    - Direct BUY
    - H4 BOS NOT required
    - Entry at Daily close
    - SL from engulfing candle wick
    """

    daily = bullish_daily_engulfing()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: {
            "valid": True,
            "trend": "RANGE",
            "setup": "BULLISH_ENGULFING",
            "direction": "BUY",
            "level": 120.0,
            "level_index": 11,
            "setup_candle_index": 11,
            "entry": 120.0,
            "reason": "Completed Daily body engulfing",
        },
    )

    monkeypatch.setattr(
        se,
        "calculate_stop_loss",
        lambda *args, **kwargs: {
            "valid": True,
            "stop_loss": 107.0,
            "reason": "Daily engulfing wick",
            "stop_reference": {
                "type": "DAILY_ENGULFING_WICK",
                "candle_index": 11,
            },
        },
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is not None
    assert result["direction"] == "BUY"
    assert result["setup"] == "BULLISH_ENGULFING"
    assert result["entry"] == 120.0
    assert result["stop_loss"] == 107.0
    assert result["tp1"] == 146.0
    assert result["tp2"] == 159.0
    assert result["rr"] == 3.0


# ============================================================
# TEST 2 — DAILY BEARISH ENGULFING
# ============================================================

def test_daily_bearish_engulfing_direct(monkeypatch):
    """
    Bearish Daily Engulfing:

    - Direct SELL
    - H4 BOS NOT required
    - Entry at Daily close
    - SL from engulfing candle wick
    """

    daily = bearish_daily_engulfing()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: {
            "valid": True,
            "trend": "RANGE",
            "setup": "BEARISH_ENGULFING",
            "direction": "SELL",
            "level": 84.0,
            "level_index": 11,
            "setup_candle_index": 11,
            "entry": 84.0,
            "reason": "Completed Daily body engulfing",
        },
    )

    monkeypatch.setattr(
        se,
        "calculate_stop_loss",
        lambda *args, **kwargs: {
            "valid": True,
            "stop_loss": 97.0,
            "reason": "Daily engulfing wick",
            "stop_reference": {
                "type": "DAILY_ENGULFING_WICK",
                "candle_index": 11,
            },
        },
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is not None
    assert result["direction"] == "SELL"
    assert result["setup"] == "BEARISH_ENGULFING"
    assert result["entry"] == 84.0
    assert result["stop_loss"] == 97.0
    assert result["tp1"] == 58.0
    assert result["tp2"] == 45.0
    assert result["rr"] == 3.0


# ============================================================
# TEST 3 — RANGE
# ============================================================

def test_range_no_signal(monkeypatch):
    """
    Genuine Daily range must produce NO SIGNAL.
    """

    daily = ranging_daily()

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is None


# ============================================================
# TEST 4 — STRUCTURAL NO BOS
# ============================================================

def test_structural_no_bos_no_signal(monkeypatch):
    """
    Structural setup exists.

    H4 BOS does not occur.

    Expected:
    NO SIGNAL.
    """

    daily = ranging_daily()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: structural_daily_stub(
            direction="BUY",
            setup="V_SHAPE",
        ),
    )

    monkeypatch.setattr(
        se,
        "detect_h4_bos",
        lambda *args, **kwargs: {
            "bos": False,
            "direction": None,
            "key_level": None,
            "broken_level": None,
            "key_level_index": None,
            "break_index": None,
            "reason": "No valid H4 BOS",
        },
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is None


# ============================================================
# TEST 5 — BOS WITHOUT RETEST
# ============================================================

def test_structural_bos_no_retest_no_signal(monkeypatch):
    """
    Structural setup + correct H4 BOS.

    No retest occurs.

    Expected:
    NO SIGNAL.
    """

    daily = ranging_daily()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: structural_daily_stub(
            direction="BUY",
            setup="V_SHAPE",
        ),
    )

    patch_pipeline(
        monkeypatch,
        bos_result=valid_bos("BUY"),
        retest_result={
            "valid": False,
            "entry": None,
            "retest_index": None,
            "confidence": 0.0,
            "reason": "No retest",
        },
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is None


# ============================================================
# TEST 6 — VALID BOS + RETEST
# ============================================================

def test_structural_valid_bos_and_retest_signal(monkeypatch):
    """
    Structural setup + correct H4 BOS + valid retest.

    Expected:
    Valid BUY signal.
    """

    daily = ranging_daily()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: structural_daily_stub(
            direction="BUY",
            setup="V_SHAPE",
        ),
    )

    patch_pipeline(
        monkeypatch,
        bos_result=valid_bos("BUY"),
        retest_result=valid_retest(),
        stop_result=valid_stop(),
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is not None
    assert result["direction"] == "BUY"
    assert result["setup"] == "V_SHAPE"
    assert result["entry"] == 100.0
    assert result["stop_loss"] == 95.0
    assert result["tp1"] == 110.0
    assert result["tp2"] == 115.0
    assert result["rr"] == 3.0


# ============================================================
# TEST 7 — WRONG BOS DIRECTION
# ============================================================

def test_structural_wrong_bos_direction_no_signal(monkeypatch):
    """
    Daily = BUY.

    H4 BOS = SELL.

    Expected:
    NO SIGNAL.
    """

    daily = ranging_daily()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: structural_daily_stub(
            direction="BUY",
            setup="V_SHAPE",
        ),
    )

    patch_pipeline(
        monkeypatch,
        bos_result=valid_bos("SELL"),
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is None


# ============================================================
# TEST 8 — FORMING CANDLES IGNORED
# ============================================================

def test_forming_candles_ignored(monkeypatch):
    """
    A forming Daily candle and forming H4 candle must never be used
    as completed candles.

    The production engine receives completed-candle data through
    get_completed_candles(). This test explicitly simulates the
    exchange returning an additional forming candle and verifies
    that the engine ignores it.
    """

    daily_completed = ranging_daily()

    forming_daily = pd.DataFrame(
        [
            [100.0, 103.0, 97.0, 101.0, 1000],
            [101.0, 104.0, 98.0, 100.5, 1000],
            [100.5, 102.5, 98.5, 101.0, 1000],
            [101.0, 103.0, 99.0, 100.5, 1000],
            [100.5, 102.5, 98.5, 101.0, 1000],
            [101.0, 103.0, 99.0, 100.5, 1000],
            [100.5, 102.5, 98.5, 101.0, 1000],
            [101.0, 103.0, 99.0, 100.5, 1000],
            [100.5, 102.5, 98.5, 101.0, 1000],
            [101.0, 103.0, 99.0, 100.5, 1000],
            [100.5, 102.5, 98.5, 101.0, 1000],
            [101.0, 103.0, 99.0, 100.5, 1000],
            # FORMING CANDLE — must be ignored
            [100.5, 150.0, 50.0, 140.0, 5000],
        ],
        index=pd.date_range(
            "2026-01-01",
            periods=13,
            freq="D",
            tz="UTC",
        ),
        columns=["open", "high", "low", "close", "volume"],
    )

    completed_h4 = base_h4()

    forming_h4 = pd.DataFrame(
        [
            [101.6, 150.0, 50.0, 119.0, 5000],
        ],
        index=pd.date_range(
            "2026-01-03",
            periods=1,
            freq="4h",
            tz="UTC",
        ),
        columns=["open", "high", "low", "close", "volume"],
    )

    market = {
        "1d": pd.concat([daily_completed, forming_daily.tail(1)]),
        "4h": pd.concat([completed_h4, forming_h4]),
    }

    original_get_completed_candles = se.get_completed_candles

    def mocked_get_completed_candles(df, *args, **kwargs):
        """
        Simulate the production candle-completion gate by removing
        the final candle from each timeframe.
        """
        if df is market["1d"] or len(df) == len(market["1d"]):
            return df.iloc[:-1].copy()

        if df is market["4h"] or len(df) == len(market["4h"]):
            return df.iloc[:-1].copy()

        return original_get_completed_candles(df, *args, **kwargs)

    monkeypatch.setattr(
        se,
        "get_completed_candles",
        mocked_get_completed_candles,
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        market,
    )

    assert result is None
# ============================================================
# TEST 9 — INVALID STRUCTURAL STOP
# ============================================================

def test_invalid_structural_stop_no_signal(monkeypatch):
    """
    Structural setup + valid BOS + valid retest.

    Stop is intentionally on the wrong side for BUY.

    Expected:
    NO SIGNAL.
    """

    daily = ranging_daily()

    monkeypatch.setattr(
        se,
        "detect_daily_setup",
        lambda *args, **kwargs: structural_daily_stub(
            direction="BUY",
            setup="V_SHAPE",
        ),
    )

    patch_pipeline(
        monkeypatch,
        bos_result=valid_bos("BUY"),
        retest_result=valid_retest(),
        stop_result=invalid_stop(),
    )

    result = se.evaluate_symbol(
        "TEST/USDT",
        valid_market(daily),
    )

    assert result is None
