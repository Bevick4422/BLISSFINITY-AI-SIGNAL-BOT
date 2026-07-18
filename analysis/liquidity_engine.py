import pandas as pd


def detect_liquidity(df: pd.DataFrame):
    """
    Detect liquidity sweeps.

    Returns:
    {
        "equal_highs": bool,
        "equal_lows": bool,
        "buy_side_sweep": bool,
        "sell_side_sweep": bool
    }
    """

    if len(df) < 8:
        return {
            "equal_highs": False,
            "equal_lows": False,
            "buy_side_sweep": False,
            "sell_side_sweep": False,
        }

    highs = df["high"].tail(6).tolist()
    lows = df["low"].tail(6).tolist()

    tolerance = 0.001

    equal_highs = abs(highs[-2] - highs[-3]) <= tolerance
    equal_lows = abs(lows[-2] - lows[-3]) <= tolerance

    buy_side_sweep = highs[-1] > max(highs[:-1])
    sell_side_sweep = lows[-1] < min(lows[:-1])

    return {
        "equal_highs": equal_highs,
        "equal_lows": equal_lows,
        "buy_side_sweep": buy_side_sweep,
        "sell_side_sweep": sell_side_sweep,
    }
