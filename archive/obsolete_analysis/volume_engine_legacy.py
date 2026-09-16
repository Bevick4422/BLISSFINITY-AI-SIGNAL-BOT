import pandas as pd


def detect_volume(df: pd.DataFrame):

    avg_volume = df["volume"].tail(20).mean()

    current_volume = df["volume"].iloc[-1]

    # Prevent division by zero
    if avg_volume <= 0:

        return {
            "volume_signal": "UNKNOWN",
            "volume_ratio": 0.0
        }

    ratio = current_volume / avg_volume

    if ratio >= 1.5:
        signal = "HIGH"

    elif ratio >= 1.0:
        signal = "NORMAL"

    else:
        signal = "LOW"

    return {
        "volume_signal": signal,
        "volume_ratio": round(float(ratio), 2)
    }


# Backward compatibility
analyze_volume = detect_volume
