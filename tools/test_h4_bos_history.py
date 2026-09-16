"""
BLISSFINITY SIGNAL
H4 BOS Historical Test

Purpose:
    Test the H4 BOS engine across historical candles.

Rules:
    - Bullish BOS = BUY
    - Bearish BOS = SELL
    - BOS requires candle CLOSE beyond confirmed swing
    - No synthetic BOS
    - No direction reversal

This file is ONLY a test.
It does not modify the strategy engine.
"""

from __future__ import annotations

from typing import Any

from market_data.fetcher import fetch_market_data
from analysis.h4_bos.h4_bos_engine import detect_h4_bos


# ==========================================================
# SETTINGS
# ==========================================================

SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
]


# ==========================================================
# PRINT RESULT
# ==========================================================

def print_result(
    symbol: str,
    result: Any,
) -> None:

    print()
    print("=" * 70)
    print(f"{symbol} | H4 BOS RESULT")
    print("=" * 70)

    print(f"BOS            : {result.get('bos')}")
    print(f"Direction      : {result.get('direction')}")
    print(f"Broken Level   : {result.get('broken_level')}")
    print(f"Swing High     : {result.get('swing_high')}")
    print(f"Swing Low      : {result.get('swing_low')}")
    print(f"Break Index    : {result.get('break_index')}")
    print(f"Swing High Idx : {result.get('swing_high_index')}")
    print(f"Swing Low Idx  : {result.get('swing_low_index')}")

    print("=" * 70)


# ==========================================================
# RUN SYMBOL
# ==========================================================

def run_symbol(symbol: str) -> None:

    print()
    print("#" * 70)
    print(f"TESTING {symbol}")
    print("#" * 70)

    try:

        market = fetch_market_data(symbol)

    except Exception as exc:

        print()
        print(f"{symbol} | MARKET DATA ERROR")
        print(f"{type(exc).__name__}: {exc}")
        return

    if not isinstance(market, dict):

        print(
            f"{symbol} | Invalid market response"
        )

        return

    h4 = market.get("4h")

    if h4 is None:

        print(
            f"{symbol} | H4 data unavailable"
        )

        return

    print(
        f"{symbol} | H4 Candles: {len(h4)}"
    )

    if len(h4) < 50:

        print(
            f"{symbol} | Not enough H4 candles"
        )

        return

    try:

        result = detect_h4_bos(h4)

    except Exception as exc:

        print()
        print(
            f"{symbol} | H4 BOS ERROR"
        )
        print(
            f"{type(exc).__name__}: {exc}"
        )

        return

    if not isinstance(result, dict):

        print(
            f"{symbol} | Invalid BOS result"
        )

        return

    print_result(
        symbol,
        result,
    )


# ==========================================================
# MAIN
# ==========================================================

def main() -> None:

    print()
    print("=" * 70)
    print("BLISSFINITY SIGNAL")
    print("H4 BOS HISTORICAL TEST")
    print("=" * 70)

    for symbol in SYMBOLS:

        run_symbol(symbol)

    print()
    print("=" * 70)
    print("H4 BOS TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
