import pandas as pd

from analysis.daily_structure.daily_structure_engine import _find_daily_rejection


def frame(rows):
    return pd.DataFrame(
        rows,
        columns=["open", "high", "low", "close", "volume"],
        index=pd.date_range("2026-01-01", periods=len(rows), freq="D"),
    )


def test_bullish_rejection_returns_buy():
    df = frame([
        [105, 106, 101, 102, 1],
        [100, 104, 99, 103, 1],  # RED -> GREEN, V level = 100
        [104, 106, 102, 105, 1],
        [103, 104, 99, 102, 1],  # touches 100, closes above
    ])
    result = _find_daily_rejection(df)
    assert result is not None
    assert result["direction"] == "BUY"
    assert result["formation_type"] == "V_SHAPE"
    assert result["level"] == 99.0


def test_bearish_rejection_returns_sell():
    df = frame([
        [100, 108, 99, 107, 1],
        [110, 112, 105, 106, 1],  # GREEN -> RED, A level = 110
        [108, 111, 104, 109, 1],
        [107, 113, 103, 106, 1],  # reaches confirmed swing high 112
    ])
    result = _find_daily_rejection(df)
    assert result is not None
    assert result["direction"] == "SELL"
    assert result["formation_type"] == "A_SHAPE"
    assert result["level"] == 112.0


def test_no_rejection_returns_none():
    df = frame([
        [100, 102, 98, 101, 1],
        [101, 104, 100, 103, 1],
        [103, 105, 102, 104, 1],
        [104, 106, 103, 105, 1],
    ])
    assert _find_daily_rejection(df) is None


def test_opposite_direction_candidates_are_ambiguous():
    df = frame([
        [102, 105, 99, 101, 1],  # red
        [100, 106, 98, 104, 1],  # green => V at 100
        [104, 112, 103, 111, 1],  # green
        [110, 111, 105, 107, 1],  # red => A at 110
        [108, 113, 97, 105, 1],  # reaches both confirmed swings
    ])
    result = _find_daily_rejection(df)
    assert result is not None
    assert result.get("ambiguous") is True


def test_opposing_candidates_return_ambiguous_without_selected_level():
    df = frame([
        [102, 105, 99, 101, 1],
        [100, 106, 98, 104, 1],  # V at 100
        [104, 112, 103, 111, 1],
        [110, 111, 105, 107, 1],  # A at 110
        [108, 113, 97, 105, 1],   # latest reaches both confirmed swings
    ])

    result = _find_daily_rejection(df)

    assert result is not None
    assert result["ambiguous"] is True
    assert result["direction"] is None
    assert result["level"] is None
    assert result["level_index"] is None


def test_ambiguous_result_is_not_required_to_have_level_index():
    df = frame([
        [102, 105, 99, 101, 1],
        [100, 106, 98, 104, 1],
        [104, 112, 103, 111, 1],
        [110, 111, 105, 107, 1],
        [108, 113, 97, 105, 1],
    ])

    result = _find_daily_rejection(df)

    assert result is not None
    if result.get("ambiguous"):
        assert result["level_index"] is None
    else:
        assert isinstance(result["level_index"], int)
        assert result["level_index"] < len(df) - 1


def test_level_touch_without_rejection_close_returns_none():
    """A level touch alone must not qualify as a rejection."""
    df = pd.DataFrame([
        {"open": 102, "high": 104, "low": 99, "close": 101},
        {"open": 100, "high": 105, "low": 98, "close": 104},
        {"open": 104, "high": 108, "low": 103, "close": 107},
        {"open": 107, "high": 110, "low": 105, "close": 109},
        # Touches the V level at 100 but closes below it
        {"open": 102, "high": 104, "low": 99, "close": 99},
    ])

    result = _find_daily_rejection(df)

    assert result is None


def test_latest_candle_is_not_used_to_create_its_own_level():
    """Only pairs completed before the latest candle may define levels."""
    df = pd.DataFrame([
        {"open": 105, "high": 108, "low": 103, "close": 104},
        {"open": 104, "high": 106, "low": 100, "close": 102},
        {"open": 102, "high": 107, "low": 101, "close": 106},
        # Latest candle creates a RED -> GREEN-like movement only
        {"open": 100, "high": 111, "low": 99, "close": 105},
    ])

    result = _find_daily_rejection(df)

    if result is not None:
        assert result["level_index"] < len(df) - 1


def test_rejected_levels_are_prior_to_latest_candle():
    df = frame([
        [105, 108, 103, 104, 1],
        [100, 106, 98, 105, 1],
        [105, 110, 104, 109, 1],
        [109, 112, 106, 107, 1],
        [107, 111, 99, 106, 1],
    ])

    result = _find_daily_rejection(df)

    if result is None:
        return

    if result.get("ambiguous"):
        assert result["level_index"] is None
        return

    assert result["level_index"] < len(df) - 1
    for item in result.get("rejected_levels", []):
        assert item["level_index"] < len(df) - 1


