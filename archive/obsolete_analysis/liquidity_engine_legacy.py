import pandas as pd


def detect_liquidity_grab(df: pd.DataFrame):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    previous_high = high.iloc[-6:-1].max()
    previous_low = low.iloc[-6:-1].min()

    current_high = high.iloc[-1]
    current_low = low.iloc[-1]
    current_close = close.iloc[-1]

    buy_side_sweep = (
        current_high > previous_high
        and current_close < previous_high
    )

    sell_side_sweep = (
        current_low < previous_low
        and current_close > previous_low
    )

    if buy_side_sweep:
        return {
            "grab": "SELL",
            "strength": 100,
            "liquidity_sweep_high": True,
            "liquidity_sweep_low": False,
        }

    if sell_side_sweep:
        return {
            "grab": "BUY",
            "strength": 100,
            "liquidity_sweep_high": False,
            "liquidity_sweep_low": True,
        }

    return {
        "grab": None,
        "strength": 0,
        "liquidity_sweep_high": False,
        "liquidity_sweep_low": False,
    }


def detect_liquidity(df: pd.DataFrame):
    """
    Legacy compatibility alias.
    """
    return detect_liquidity_grab(df)


__all__ = [
    "detect_liquidity_grab",
    "detect_liquidity",
]
