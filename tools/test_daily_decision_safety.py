"""
============================================================
BLISSFINITY SIGNAL
Daily Decision Safety Tests
============================================================

Purpose
-------
Verify that Daily Engulfing remains the primary direction.

Rules
-----
Bullish Engulfing -> BUY
Bearish Engulfing -> SELL

An older opposing Daily structural situation must NOT
automatically reverse the current Daily Engulfing direction.

The Strategy Engine must never manufacture a reversal.

If the Daily Setup Engine itself reports no valid setup,
the Strategy Engine must return no signal.
"""

from __future__ import annotations

import pandas as pd

import engine.strategy_engine as strategy_engine


def make_daily(candles=50):
    rows = []

    for i in range(candles):
        rows.append({
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 100.0,
            "volume": 1000.0,
        })

    return pd.DataFrame(rows)


def make_h4(candles=100):
    rows = []

    for i in range(candles):
        rows.append({
            "open": 100.0,
            "high": 105.0,
            "low": 95.0,
            "close": 101.0,
            "volume": 1000.0,
        })

    return pd.DataFrame(rows)


def run_engine(monkeypatch, setup):
    monkeypatch.setattr(
        strategy_engine,
        "detect_daily_setup",
        lambda df: setup,
    )

    return strategy_engine.evaluate_symbol(
        "TEST/USDT:USDT",
        {
            "1d": make_daily(),
            "4h": make_h4(),
        },
    )


def test_bullish_engulfing_keeps_buy(monkeypatch):
    setup = {
        "valid": True,
        "setup": "Bullish Engulfing",
        "direction": "BUY",
        "level": 100.0,
        "level_index": 49,
        "entry": 101.0,
    }

    signal = run_engine(monkeypatch, setup)

    assert signal is not None
    assert signal["direction"] == "BUY"
    assert signal["setup"] == "Bullish Engulfing"
    assert signal["entry_type"] == "ENGULFING"


def test_bearish_engulfing_keeps_sell(monkeypatch):
    setup = {
        "valid": True,
        "setup": "Bearish Engulfing",
        "direction": "SELL",
        "level": 100.0,
        "level_index": 49,
        "entry": 99.0,
    }

    signal = run_engine(monkeypatch, setup)

    assert signal is not None
    assert signal["direction"] == "SELL"
    assert signal["setup"] == "Bearish Engulfing"
    assert signal["entry_type"] == "ENGULFING"


def test_invalid_daily_setup_returns_no_signal(monkeypatch):
    setup = {
        "valid": False,
        "setup": None,
        "direction": None,
        "level": None,
        "level_index": None,
        "entry": None,
    }

    signal = run_engine(monkeypatch, setup)

    assert signal is None


def test_daily_engulfing_does_not_call_h4_bos(monkeypatch):
    setup = {
        "valid": True,
        "setup": "Bearish Engulfing",
        "direction": "SELL",
        "level": 100.0,
        "level_index": 49,
        "entry": 99.0,
    }

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "H4 BOS must not be called for Daily Engulfing"
        )

    monkeypatch.setattr(
        strategy_engine,
        "detect_h4_bos",
        fail_if_called,
    )

    signal = run_engine(monkeypatch, setup)

    assert signal is not None
    assert signal["direction"] == "SELL"


def test_engine_has_no_daily_structural_reversal_layer():
    source = open(
        "engine/strategy_engine.py",
        "r",
        encoding="utf-8",
    ).read()

    forbidden = (
        "_evaluate_daily_structural_reversal",
        "CONFIRMED DAILY STRUCTURAL REVERSAL",
        "ACTION          : REVERSE DAILY DIRECTION",
        "BEARISH_DAILY_BREAK_RETEST",
        "BULLISH_DAILY_BREAK_RETEST",
    )

    for item in forbidden:
        assert item not in source, (
            f"Legacy Daily reversal logic still present: {item}"
        )
