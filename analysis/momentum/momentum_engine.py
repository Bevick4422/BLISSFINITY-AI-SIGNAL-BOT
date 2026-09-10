
"""
BLISSFINITY AI SIGNAL BOT
MOMENTUM ENGINE
"""

import pandas as pd


def detect_momentum(df: pd.DataFrame):
    """
    Detect momentum using EMA slope,
    RSI and Volume.
    """

    close = df["close"]

    volume = df["volume"]

    # -----------------------------
    # EMA Momentum
    # -----------------------------

    ema20 = close.ewm(span=20).mean()

    ema_now = ema20.iloc[-1]

    ema_prev = ema20.iloc[-2]

    # -----------------------------
    # RSI
    # -----------------------------

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    current_rsi = float(rsi.iloc[-1])

    # -----------------------------
    # Volume
    # -----------------------------

    avg_volume = volume.rolling(20).mean().iloc[-1]

    current_volume = volume.iloc[-1]

    volume_ok = current_volume > avg_volume

    # -----------------------------
    # Momentum Decision
    # -----------------------------

    if ema_now > ema_prev and current_rsi > 55 and volume_ok:

        momentum = "BULLISH"

    elif ema_now < ema_prev and current_rsi < 45 and volume_ok:

        momentum = "BEARISH"

    else:

        momentum = "NEUTRAL"

    return {

        "momentum": momentum,

        "rsi": round(current_rsi, 2),

        "volume_confirmation": volume_ok,

        "ema_slope": round(float(ema_now - ema_prev), 4)

    }

# Compatibility alias
analyze_momentum = detect_momentum


# Compatibility alias
analyze_momentum = detect_momentum
