"""
BLISSFINITY SIGNAL
Completed Candle Gate

The strategy may use ONLY completed Daily and H4 candles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd


_TIMEFRAME_SECONDS = {
    "4h": 4 * 60 * 60,
    "1d": 24 * 60 * 60,
}


def _normalise_index(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if isinstance(result.index, pd.DatetimeIndex):
        index = pd.to_datetime(
            result.index,
            utc=True,
            errors="coerce",
        )
    elif "timestamp" in result.columns:
        index = pd.to_datetime(
            result["timestamp"],
            utc=True,
            errors="coerce",
        )
    else:
        index = pd.to_datetime(
            result.index,
            unit="ms",
            utc=True,
            errors="coerce",
        )

    if index.isna().any():
        raise ValueError("Invalid candle timestamps")

    result.index = index
    result = result[~result.index.duplicated(keep="last")]

    return result.sort_index()


def get_completed_candles(
    df: pd.DataFrame,
    timeframe: str,
    now: Optional[datetime] = None,
) -> pd.DataFrame:
    """Return only candles whose complete interval has elapsed."""

    timeframe = str(timeframe).strip().lower()

    if timeframe not in _TIMEFRAME_SECONDS:
        raise ValueError("Only 4h and 1d are supported")

    if df is None or df.empty:
        return pd.DataFrame()

    required = {
        "open",
        "high",
        "low",
        "close",
        "volume",
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing OHLCV columns: {sorted(missing)}"
        )

    result = _normalise_index(df)

    if now is None:
        now_utc = datetime.now(timezone.utc)
    else:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")

        now_utc = now.astimezone(timezone.utc)

    duration = pd.Timedelta(
        seconds=_TIMEFRAME_SECONDS[timeframe]
    )

    cutoff = pd.Timestamp(now_utc)

    mask = (result.index + duration) <= cutoff

    return result.loc[mask].copy()


__all__ = ["get_completed_candles"]