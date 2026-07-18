
"""
BLISSFINITY AI SIGNAL BOT
ELLIOTT WAVE ENGINE
"""

import pandas as pd


def detect_wave(df: pd.DataFrame):
    """
    Estimate the current Elliott Wave phase.
    """

    close = df["close"]

    ema20 = close.ewm(span=20).mean()

    current = close.iloc[-1]
    previous = close.iloc[-6]

    change = ((current - previous) / previous) * 100

    # Strong impulsive move
    if change > 4:
        wave = "WAVE_3"
        phase = "IMPULSE"

    # Pullback
    elif change > 1:
        wave = "WAVE_2"
        phase = "CORRECTION"

    # Strong bearish impulse
    elif change < -4:
        wave = "ABC"
        phase = "CORRECTION"

    else:
        wave = "WAVE_4"
        phase = "CONSOLIDATION"

    return {

        "wave": wave,

        "phase": phase,

        "strength": round(abs(change), 2),

        "ema20": round(float(ema20.iloc[-1]), 2)

    }