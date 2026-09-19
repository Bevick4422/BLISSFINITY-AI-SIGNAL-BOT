import pandas as pd

from analysis.daily_structure.daily_structure_engine import (
    _find_va,
    _find_latest_va_levels,
    _find_daily_rejection,
    detect_daily_setup,
)


def make_df(rows):
    return pd.DataFrame(
        rows,
        columns=["open", "high", "low", "close", "volume"],
        index=pd.date_range("2026-01-01", periods=len(rows), freq="D"),
    )


def test_va_finder_selects_latest_bullish_v_pair():
    df = make_df([
        [10, 11, 9, 9.5, 100],
        [9.5, 10, 8, 8.5, 100],
        [8.5, 10, 8, 9.5, 100],
        [9.5, 11, 9, 10.5, 100],
    ])

    result = _find_va(df, "BULLISH")

    assert result is not None
    assert result["formation_type"] == "V_SHAPE"
    assert result["direction"] == "BUY"
    assert result["second_candle_index"] == 2
    assert result["level"] == 8.5


def test_va_finder_selects_latest_bearish_a_pair():
    df = make_df([
        [10, 11, 9, 10.5, 100],
        [10.5, 12, 10, 11.5, 100],
        [11.5, 12, 10, 10.5, 100],
        [10.5, 11, 9, 9.5, 100],
    ])

    result = _find_va(df, "BEARISH")

    assert result is not None
    assert result["formation_type"] == "A_SHAPE"
    assert result["direction"] == "SELL"
    assert result["second_candle_index"] == 2
    assert result["level"] == 11.5


def test_va_finder_rejects_v_when_trend_is_not_bullish():
    df = make_df([
        [10, 11, 9, 9.5, 100],
        [9.5, 10, 8, 8.5, 100],
    ])

    assert _find_va(df, "RANGE") is None


def test_va_finder_rejects_a_when_trend_is_not_bearish():
    df = make_df([
        [10, 11, 9, 10.5, 100],
        [10.5, 12, 10, 11.5, 100],
    ])

    assert _find_va(df, "RANGE") is None


def test_latest_va_levels_detects_a_and_v_independently():
    df = make_df([
        [10, 11, 9, 9.5, 100],    # RED
        [9.5, 10, 8, 9.8, 100],   # GREEN
        [9.8, 11, 9, 10.8, 100],  # GREEN
        [10.8, 12, 10, 10.2, 100],# RED
    ])

    result = _find_latest_va_levels(df)

    assert result["V_SHAPE"] is not None
    assert result["A_SHAPE"] is not None
    assert result["V_SHAPE"]["level"] == 9.5
    assert result["A_SHAPE"]["level"] == 10.8


def test_va_finder_returns_none_when_no_matching_pair_for_trend():
    df = make_df([
        [10, 11, 9, 10.5, 100],
        [10.5, 12, 10, 11.5, 100],
        [11.5, 13, 11, 12.5, 100],
    ])

    assert _find_va(df, "BULLISH") is None
    assert _find_va(df, "BEARISH") is None
