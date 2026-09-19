from tools.test_va_detector import make_df
from analysis.daily_structure.daily_structure_engine import _find_va


def test_va_finder_selects_latest_bullish_v_pair():
    df = make_df([
        [10, 11, 9, 9.5, 100],   # RED
        [9.5, 10, 8, 8.5, 100],  # RED
        [8.5, 10, 8, 9.5, 100], # GREEN: V at index 2
        [9.5, 10, 9, 9.2, 100], # RED
        [9.2, 11, 9, 10.5, 100],# GREEN: later V at index 4
    ])

    result = _find_va(df, "BULLISH")

    assert result is not None
    assert result["formation_type"] == "V_SHAPE"
    assert result["direction"] == "BUY"
    assert result["second_candle_index"] == 4
    assert result["level"] == 9.2


def test_va_finder_selects_latest_bearish_a_pair():
    df = make_df([
        [10, 11, 9, 10.5, 100],  # GREEN
        [10.5, 12, 10, 11.5, 100],# GREEN
        [11.5, 12, 10, 10.5, 100],# RED: A at index 2
        [10.5, 11, 10, 10.8, 100],# GREEN
        [10.8, 11, 9, 9.5, 100], # RED: later A at index 4
    ])

    result = _find_va(df, "BEARISH")

    assert result is not None
    assert result["formation_type"] == "A_SHAPE"
    assert result["direction"] == "SELL"
    assert result["second_candle_index"] == 4
    assert result["level"] == 10.8
