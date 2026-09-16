import pandas as pd

from analysis.h4_bos.h4_bos_engine import detect_h4_bos


def make_bearish_bos_data():
    rows = [
        (100, 104, 98, 102),
        (102, 106, 100, 104),
        (104, 108, 101, 106),
        (106, 108, 90, 100),
        (100, 103, 94, 99),
        (99, 110, 96, 108),
        (108, 120, 107, 116),
        (116, 118, 109, 112),
        (112, 114, 106, 110),
        (110, 113, 101, 105),
        (105, 108, 92, 88),
        (88, 94, 84, 90),
        (90, 96, 87, 92),
        (92, 98, 89, 94),
    ]

    return pd.DataFrame(
        rows,
        columns=["open", "high", "low", "close"],
    ).assign(volume=1000.0)


def make_wick_only_data():
    rows = [
        (100, 104, 98, 102),
        (102, 106, 100, 104),
        (104, 108, 101, 106),
        (106, 108, 90, 100),
        (100, 103, 94, 99),
        (99, 110, 96, 108),
        (108, 120, 107, 116),
        (116, 118, 109, 112),
        (112, 114, 106, 110),
        (110, 113, 101, 105),
        (105, 115, 88, 106),
        (106, 110, 94, 102),
        (102, 108, 96, 104),
        (104, 109, 98, 105),
    ]

    return pd.DataFrame(
        rows,
        columns=["open", "high", "low", "close"],
    ).assign(volume=1000.0)


def test_bearish_h4_bos():
    df = make_bearish_bos_data()

    result = detect_h4_bos(df)

    assert result["bos"] is True
    assert result["direction"] == "SELL"
    assert result["body_crossed"] is True
    assert result["close_beyond"] is True
    assert result["key_level"] == 90.0
    assert result["break_index"] == 10


def test_wick_only_break_is_invalid():
    df = make_wick_only_data()

    result = detect_h4_bos(df)

    assert result["bos"] is False


if __name__ == "__main__":
    test_bearish_h4_bos()
    test_wick_only_break_is_invalid()
    print("H4 BOS TEST: PASS")
