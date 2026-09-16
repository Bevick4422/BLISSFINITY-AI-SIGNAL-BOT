"""
============================================================
BLISSFINITY SIGNAL
Daily Structural Reversal Tests
============================================================

Tests the new Daily-only structural override.

RULE:

Bullish Daily Engulfing
        +
Bearish Daily Break + Retest
        ->
SELL

Bearish Daily Engulfing
        +
Bullish Daily Break + Retest
        ->
BUY

Opposing break WITHOUT retest
        ->
original engulfing direction survives

No opposing structure
        ->
original engulfing direction survives

IMPORTANT:
H4 BOS must NOT participate in the Daily reversal path.
"""

from __future__ import annotations

import pandas as pd
import pytest

import engine.strategy_engine as strategy


# ============================================================
# DATA
# ============================================================

def make_daily(
    direction: str = "BUY",
    count: int = 12,
):
    """
    Create completed Daily candles.

    The exact OHLC values are intentionally simple because
    these tests isolate the strategy-engine decision layer.
    """

    rows = []

    for i in range(count - 2):
        rows.append(
            {
                "open": 100.0,
                "high": 105.0,
                "low": 95.0,
                "close": 102.0,
            }
        )

    if direction == "BUY":

        # Previous RED candle
        rows.append(
            {
                "open": 105.0,
                "high": 106.0,
                "low": 94.0,
                "close": 96.0,
            }
        )

        # Current GREEN engulfing candle
        rows.append(
            {
                "open": 95.0,
                "high": 115.0,
                "low": 93.0,
                "close": 108.0,
            }
        )

    else:

        # Previous GREEN candle
        rows.append(
            {
                "open": 95.0,
                "high": 106.0,
                "low": 94.0,
                "close": 105.0,
            }
        )

        # Current RED engulfing candle
        rows.append(
            {
                "open": 106.0,
                "high": 108.0,
                "low": 88.0,
                "close": 94.0,
            }
        )

    return pd.DataFrame(
        rows,
        index=pd.date_range(
            "2026-01-01",
            periods=len(rows),
            freq="D",
            tz="UTC",
        ),
    )


def make_h4():
    return pd.DataFrame(
        {
            "open": [100.0] * 12,
            "high": [105.0] * 12,
            "low": [95.0] * 12,
            "close": [101.0] * 12,
        },
        index=pd.date_range(
            "2026-01-01",
            periods=12,
            freq="4h",
            tz="UTC",
        ),
    )


# ============================================================
# DAILY SETUP STUBS
# ============================================================

def bullish_engulfing_setup():
    return {
        "valid": True,
        "trend": "BULLISH",
        "setup": "Bullish Engulfing",
        "direction": "BUY",
        "level": 100.0,
        "level_index": 5,
        "setup_candle_index": 11,
        "setup_candle_timestamp":
            pd.Timestamp(
                "2026-01-12",
                tz="UTC",
            ),
        "entry": 108.0,
        "retest_required": False,
        "entry_mode": "DAILY_CLOSE",
    }


def bearish_engulfing_setup():
    return {
        "valid": True,
        "trend": "BEARISH",
        "setup": "Bearish Engulfing",
        "direction": "SELL",
        "level": 100.0,
        "level_index": 5,
        "setup_candle_index": 11,
        "setup_candle_timestamp":
            pd.Timestamp(
                "2026-01-12",
                tz="UTC",
            ),
        "entry": 94.0,
        "retest_required": False,
        "entry_mode": "DAILY_CLOSE",
    }


# ============================================================
# STRUCTURAL BREAK STUBS
# ============================================================

def bearish_daily_break():
    return {
        "valid": True,
        "direction": "SELL",
        "key_level": 100.0,
        "key_level_index": 6,
        "break_index": 8,
        "break_timestamp":
            pd.Timestamp(
                "2026-01-09",
                tz="UTC",
            ),
        "break_price": 94.0,
        "structural_extreme": 110.0,
        "structural_extreme_index": 7,
        "reason":
            "Completed Daily body broke protected low",
    }


def bullish_daily_break():
    return {
        "valid": True,
        "direction": "BUY",
        "key_level": 100.0,
        "key_level_index": 6,
        "break_index": 8,
        "break_timestamp":
            pd.Timestamp(
                "2026-01-09",
                tz="UTC",
            ),
        "break_price": 106.0,
        "structural_extreme": 90.0,
        "structural_extreme_index": 7,
        "reason":
            "Completed Daily body broke protected high",
    }


# ============================================================
# RETEST STUBS
# ============================================================

def valid_daily_bearish_retest():
    return {
        "valid": True,
        "direction": "SELL",
        "entry": 99.0,
        "retest_index": 10,
        "confidence": 88.0,
        "stop_reference": {
            "type":
                "DAILY_KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 6,
        },
        "reason":
            "Daily bearish break retested",
    }


def valid_daily_bullish_retest():
    return {
        "valid": True,
        "direction": "BUY",
        "entry": 101.0,
        "retest_index": 10,
        "confidence": 88.0,
        "stop_reference": {
            "type":
                "DAILY_KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 6,
        },
        "reason":
            "Daily bullish break retested",
    }


def invalid_daily_retest():
    return {
        "valid": False,
        "entry": None,
        "reason":
            "NO DAILY RETEST",
    }


# ============================================================
# TEST 1
# ============================================================

def test_bullish_engulfing_opposing_daily_bearish_break_retest(
    monkeypatch,
):
    """
    Bullish Engulfing candidate must reverse to SELL when
    opposing Daily bearish break + retest is confirmed.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    monkeypatch.setattr(
        strategy,
        "detect_break_retest",
        lambda **kwargs:
            valid_daily_bearish_retest(),
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is not None
    assert result["valid"] is True
    assert result["direction"] == "SELL"
    assert result["entry"] == 99.0
    assert result["key_level"] == 100.0
    assert result["break_index"] == 8
    assert result["retest_index"] == 10


# ============================================================
# TEST 2
# ============================================================

def test_bearish_engulfing_opposing_daily_bullish_break_retest(
    monkeypatch,
):
    """
    Bearish Engulfing candidate must reverse to BUY when
    opposing Daily bullish break + retest is confirmed.
    """

    daily = make_daily("SELL")

    setup = bearish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bullish_daily_break(),
    )

    monkeypatch.setattr(
        strategy,
        "detect_break_retest",
        lambda **kwargs:
            valid_daily_bullish_retest(),
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is not None
    assert result["valid"] is True
    assert result["direction"] == "BUY"
    assert result["entry"] == 101.0
    assert result["key_level"] == 100.0
    assert result["break_index"] == 8
    assert result["retest_index"] == 10


# ============================================================
# TEST 3
# ============================================================

def test_opposing_daily_break_without_retest_does_not_reverse(
    monkeypatch,
):
    """
    Opposing Daily break alone is NOT enough.

    No retest -> no reversal.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    monkeypatch.setattr(
        strategy,
        "detect_break_retest",
        lambda **kwargs:
            invalid_daily_retest(),
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is None


# ============================================================
# TEST 4
# ============================================================

def test_no_opposing_daily_structure_preserves_candidate(
    monkeypatch,
):
    """
    No opposing Daily structure -> no reversal.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            None,
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is None


# ============================================================
# TEST 5
# ============================================================

def test_daily_reversal_does_not_call_h4_bos(
    monkeypatch,
):
    """
    Daily structural reversal must be completely independent
    of the H4 BOS engine.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    monkeypatch.setattr(
        strategy,
        "detect_break_retest",
        lambda **kwargs:
            valid_daily_bearish_retest(),
    )

    def fail_if_called(*args, **kwargs):
        pytest.fail(
            "H4 BOS must not be called during Daily reversal"
        )

    monkeypatch.setattr(
        strategy,
        "detect_h4_bos",
        fail_if_called,
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is not None
    assert result["direction"] == "SELL"


# ============================================================
# TEST 6
# ============================================================

def test_invalid_daily_direction_has_no_reversal(
    monkeypatch,
):
    """
    Invalid Daily direction must never create a reversal.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()
    setup["direction"] = None

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is None


# ============================================================
# TEST 7
# ============================================================

def test_missing_setup_index_has_no_reversal(
    monkeypatch,
):
    """
    A reversal requires a valid Daily setup candle index.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()
    setup["setup_candle_index"] = None
    setup["level_index"] = None

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is None


# ============================================================
# TEST 8
# ============================================================

def test_daily_retest_direction_must_match_opposing_structure(
    monkeypatch,
):
    """
    A retest with the wrong direction must not create a
    Daily reversal.
    """

    daily = make_daily("BUY")

    setup = bullish_engulfing_setup()

    monkeypatch.setattr(
        strategy,
        "_find_latest_daily_break",
        lambda *args, **kwargs:
            bearish_daily_break(),
    )

    monkeypatch.setattr(
        strategy,
        "detect_break_retest",
        lambda **kwargs: {
            "valid": True,
            "direction": "BUY",
            "entry": 101.0,
            "retest_index": 10,
            "confidence": 88.0,
            "stop_reference": {
                "type":
                    "DAILY_KEY_LEVEL_ESTABLISHING_WICK",
                "level_index": 6,
            },
        },
    )

    result = strategy._evaluate_daily_structural_reversal(
        daily=daily,
        daily_setup=setup,
    )

    assert result is not None
    assert result["direction"] == "SELL"


print(
    "DAILY STRUCTURAL REVERSAL TEST MODULE: READY"
)
