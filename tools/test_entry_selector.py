"""
=========================================================
BLISSFINITY SIGNAL
Entry Selector Production Test
=========================================================

Production path:

Market Data
    ↓
Daily Setup
    ↓
Daily Entry / Daily Level
    ↓
H4 Structure
    ↓
Entry Selector
=========================================================
"""

from __future__ import annotations

from market_data.fetcher import fetch_market_data
from analysis.daily_setup.daily_engine import detect_daily_setup
from analysis.entry.entry_selector import select_best_entry


SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
]


def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def test_symbol(symbol: str) -> None:

    print_header(
        f"{symbol} | ENTRY SELECTOR PRODUCTION TEST"
    )

    # =====================================================
    # MARKET DATA
    # =====================================================

    market = fetch_market_data(symbol)

    if market is None:
        print("RESULT: MARKET DATA UNAVAILABLE")
        return

    daily = market["1d"]
    h4 = market["4h"]

    print()
    print("[1] MARKET DATA")
    print(f"Daily candles : {len(daily)}")
    print(f"H4 candles    : {len(h4)}")

    # =====================================================
    # DAILY SETUP
    # =====================================================

    print()
    print("[2] DAILY SETUP")

    setup = detect_daily_setup(daily)

    direction = setup.get("direction")
    setup_name = setup.get("setup")
    level = setup.get("level")
    level_index = setup.get("level_index")
    daily_entry = setup.get("entry")
    valid = setup.get("valid")

    print(f"Direction     : {direction}")
    print(f"Setup         : {setup_name}")
    print(f"Level         : {level}")
    print(f"Level Index   : {level_index}")
    print(f"Daily Entry   : {daily_entry}")
    print(f"Valid         : {valid}")

    # =====================================================
    # VALIDATE DAILY SETUP
    # =====================================================

    if not valid:
        print()
        print("RESULT: NO VALID DAILY SETUP")
        return

    if direction not in ("BUY", "SELL"):
        print()
        print("RESULT: INVALID DIRECTION")
        return

    # =====================================================
    # DAILY ENGULFING
    # =====================================================

    if setup_name in (
        "Bullish Engulfing",
        "Bearish Engulfing",
    ):

        if daily_entry is None:
            print()
            print("RESULT: INVALID DAILY ENGULFING ENTRY")
            return

        print()
        print("[3] ENTRY SELECTOR")
        print("Daily Engulfing setup detected.")
        print(f"Setup       : {setup_name}")
        print(f"Direction   : {direction}")
        print(f"Daily Entry : {daily_entry}")

        result = select_best_entry(
            df=h4,
            setup=setup_name,
            direction=direction,
            daily_entry=daily_entry,
        )

    # =====================================================
    # V / A STRUCTURE
    # =====================================================

    elif setup_name in (
        "V Shape",
        "A Shape",
    ):

        if level is None:
            print()
            print("RESULT: NO DAILY LEVEL")
            return

        if level_index is None:
            print()
            print("RESULT: NO DAILY LEVEL INDEX")
            return

        print()
        print("[3] ENTRY SELECTOR")
        print(f"Setup       : {setup_name}")
        print(f"Direction   : {direction}")
        print(f"Level       : {level}")
        print(f"Level Index : {level_index}")

        result = select_best_entry(
            df=h4,
            setup=setup_name,
            direction=direction,
            level=level,
            level_index=level_index,
        )

    else:

        print()
        print(
            f"RESULT: UNSUPPORTED DAILY SETUP: "
            f"{setup_name}"
        )
        return

    # =====================================================
    # RESULT
    # =====================================================

    print()
    print("[4] FINAL ENTRY RESULT")

    print(
        f"Entry Type  : "
        f"{result.get('entry_type')}"
    )

    print(
        f"Entry Price : "
        f"{result.get('entry_price')}"
    )

    print(
        f"Entry Data  : "
        f"{result.get('entry_data')}"
    )

    # =====================================================
    # STATUS
    # =====================================================

    entry_data = result.get(
        "entry_data",
        {},
    )

    if entry_data.get("valid"):

        print()
        print("RESULT: VALID ENTRY FOUND")

    else:

        print()
        print("RESULT: NO VALID ENTRY")


def main() -> None:

    print_header(
        "BLISSFINITY SIGNAL | ENTRY SELECTOR TEST"
    )

    for symbol in SYMBOLS:

        try:
            test_symbol(symbol)

        except Exception as exc:

            print()
            print("=" * 70)
            print(f"{symbol} | TEST ERROR")
            print("=" * 70)
            print(f"Error: {exc}")

    print_header(
        "ENTRY SELECTOR TEST COMPLETE"
    )


if __name__ == "__main__":
    main()