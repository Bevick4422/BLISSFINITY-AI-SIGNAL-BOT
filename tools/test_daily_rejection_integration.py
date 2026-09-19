import pandas as pd
import pytest

import engine.strategy_engine as strategy


@pytest.fixture
def setup_engine(monkeypatch):
    """Isolate strategy routing from live market data and risk calculations."""
    daily = pd.DataFrame(
        [{"open": 100, "high": 105, "low": 95, "close": 102}]
        * 10
    )
    h4 = pd.DataFrame(
        [{"open": 100, "high": 105, "low": 95, "close": 102}]
        * 20
    )

    monkeypatch.setattr(
        strategy, "validate_market_data", lambda data: True
    )
    monkeypatch.setattr(
        strategy, "get_completed_candles",
        lambda df, timeframe: df
    )
    monkeypatch.setattr(
        strategy, "get_current_price", lambda df: 102.0
    )

    captured = {}

    def fake_build_final_signal(**kwargs):
        captured.update(kwargs)
        return {"test_signal": True, **kwargs}

    monkeypatch.setattr(
        strategy, "_build_final_signal", fake_build_final_signal
    )

    market_data = {"1d": daily, "4h": h4}

    return {
        "daily": daily,
        "h4": h4,
        "market_data": market_data,
        "captured": captured,
    }


def daily_rejection(direction="BUY", setup="V_SHAPE"):
    return {
        "valid": True,
        "trend": "BULLISH" if direction == "BUY" else "BEARISH",
        "setup": setup,
        "direction": direction,
        "level": 100.0,
        "level_index": 5,
        "setup_candle_index": 9,
        "entry": None,
        "retest_required": True,
        "entry_mode": "H4_PATHWAY",
        "reason": "DAILY_REJECTION_REQUIRES_MATCHING_H4_BOS_AND_RETEST",
    }


def valid_bos(direction="BUY"):
    return {
        "bos": True,
        "direction": direction,
        "key_level": 101.0,
        "key_level_index": 8,
        "break_index": 12,
    }


def valid_retest():
    return {
        "valid": True,
        "entry": 101.0,
        "retest_index": 15,
        "confidence": 80,
        "stop_reference": {
            "type": "H4_KEY_LEVEL_ESTABLISHING_WICK",
            "level_index": 8,
        },
    }


def test_daily_rejection_routes_to_matching_bos_and_retest(
    monkeypatch, setup_engine
):
    ctx = setup_engine
    monkeypatch.setattr(
        strategy, "detect_daily_setup",
        lambda df: daily_rejection("BUY", "V_SHAPE")
    )
    monkeypatch.setattr(
        strategy, "detect_h4_bos", lambda df: valid_bos("BUY")
    )

    retest_calls = []

    def fake_retest(**kwargs):
        retest_calls.append(kwargs)
        return valid_retest()

    monkeypatch.setattr(
        strategy, "detect_break_retest", fake_retest
    )

    result = strategy.evaluate_symbol("TEST/USDT", ctx["market_data"])

    assert result is not None
    assert result["test_signal"] is True
    assert result["entry_type"] == "BREAK_RETEST"
    assert result["direction"] == "BUY"
    assert len(retest_calls) == 1
    assert retest_calls[0]["level"] == 101.0
    assert retest_calls[0]["direction"] == "BUY"
    assert retest_calls[0]["bos_index"] == 12


def test_daily_rejection_wrong_bos_direction_is_blocked(
    monkeypatch, setup_engine
):
    ctx = setup_engine
    monkeypatch.setattr(
        strategy, "detect_daily_setup",
        lambda df: daily_rejection("BUY", "V_SHAPE")
    )
    monkeypatch.setattr(
        strategy, "detect_h4_bos", lambda df: valid_bos("SELL")
    )

    retest_called = []
    monkeypatch.setattr(
        strategy, "detect_break_retest",
        lambda **kwargs: retest_called.append(kwargs)
    )

    result = strategy.evaluate_symbol("TEST/USDT", ctx["market_data"])

    assert result is None
    assert retest_called == []


def test_daily_rejection_without_retest_is_blocked(
    monkeypatch, setup_engine
):
    ctx = setup_engine
    monkeypatch.setattr(
        strategy, "detect_daily_setup",
        lambda df: daily_rejection("BUY", "V_SHAPE")
    )
    monkeypatch.setattr(
        strategy, "detect_h4_bos", lambda df: valid_bos("BUY")
    )
    monkeypatch.setattr(
        strategy, "detect_break_retest",
        lambda **kwargs: {
            "valid": False,
            "reason": "NO REQUIRED H4 RETEST",
        }
    )

    result = strategy.evaluate_symbol("TEST/USDT", ctx["market_data"])

    assert result is None


def test_ambiguous_daily_rejection_is_blocked_before_h4(
    monkeypatch, setup_engine
):
    ctx = setup_engine
    monkeypatch.setattr(
        strategy, "detect_daily_setup",
        lambda df: {
            "valid": True,
            "trend": "BULLISH",
            "setup": None,
            "direction": None,
            "reason": "DAILY_REJECTION_AMBIGUOUS_LEVELS_NO_SIGNAL",
        }
    )

    h4_called = []
    monkeypatch.setattr(
        strategy, "detect_h4_bos",
        lambda df: h4_called.append(True)
    )

    result = strategy.evaluate_symbol("TEST/USDT", ctx["market_data"])

    assert result is None
    assert h4_called == []


@pytest.mark.parametrize(
    "setup,direction",
    [
        ("Bullish Engulfing", "BUY"),
        ("Bearish Engulfing", "SELL"),
    ],
)
def test_engulfing_still_routes_directly_without_h4_bos(
    monkeypatch, setup_engine, setup, direction
):
    ctx = setup_engine
    monkeypatch.setattr(
        strategy, "detect_daily_setup",
        lambda df: {
            "valid": True,
            "trend": "RANGE",
            "setup": setup,
            "direction": direction,
            "level": 100.0,
            "level_index": 5,
            "setup_candle_index": 9,
            "entry": 102.0,
        }
    )

    h4_called = []
    monkeypatch.setattr(
        strategy, "detect_h4_bos",
        lambda df: h4_called.append(True)
    )

    result = strategy.evaluate_symbol("TEST/USDT", ctx["market_data"])

    assert result is not None
    assert result["entry_type"] == "ENGULFING"
    assert result["direction"] == direction
    assert h4_called == []
