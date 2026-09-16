"""
Wave Engine Template
"""

import pandas as pd


def detect_wave(df: pd.DataFrame):
    """
    Very simple Elliott Wave estimation.
    This will later become the advanced version.
    """

    if len(df) < 20:
        return {
            "wave": "UNKNOWN"
        }

    highs = df["high"]
    lows = df["low"]

    if highs.iloc[-1] > highs.iloc[-5]:
        return {
            "wave": "IMPULSE"
        }

    return {
        "wave": "CORRECTIVE"
    }
