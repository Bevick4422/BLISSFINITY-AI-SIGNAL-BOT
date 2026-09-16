import pandas as pd

from analysis.atr.atr_engine import calculate_atr


def test_atr():
    df = pd.DataFrame(
        {
            "high": [110.0, 115.0, 120.0, 125.0, 130.0],
            "low": [100.0, 105.0, 110.0, 115.0, 120.0],
            "close": [105.0, 112.0, 117.0, 122.0, 127.0],
        }
    )

    result = calculate_atr(df, period=3)

    assert result == 10.0


if __name__ == "__main__":
    test_atr()
    print("ATR TEST: PASS")
