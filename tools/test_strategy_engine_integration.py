"""
=============================================================
BLISSFINITY SIGNAL
Strategy Engine Integration Test
=============================================================

Purpose
-------
Verify that the existing Strategy Engine correctly connects:

    Market Data
        ↓
    Daily Setup
        ↓
    H4 BOS
        ↓
    Entry Selection
        ↓
    Final Strategy Signal

This test does NOT modify production code.

It only verifies the current interface of:

    engine.strategy_engine.evaluate_symbol()

Important
---------
A "NO VALID ENTRY" result is acceptable.

The strategy engine must NOT manufacture a signal when
the market structure does not provide a valid entry.
"""

from __future__ import annotations

import traceback

import pandas as pd

from engine.strategy_engine import evaluate_symbol


# ============================================================
# TEST SETTINGS
# ============================================================

SYMBOL = "TEST/BTC"


# ============================================================
# MARKET DATA
# ============================================================

def create_daily_data(
    candles: int = 250,
) -> pd.DataFrame:
    """
    Create deterministic Daily OHLCV data.

    The data is intentionally simple because this test is
    focused on the Strategy Engine interface rather than
    testing MEXC connectivity.
    """

    rows = []

    price = 100.0

    for _ in range(candles):

        open_price = price

        high = price + 4.0

        low = price - 4.0

        close = price + 1.0

        rows.append(
            {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1000.0,
            }
        )

        price = close

    return pd.DataFrame(rows)


def create_h4_data(
    candles: int = 300,
) -> pd.DataFrame:
    """
    Create deterministic H4 OHLCV data.

    The final candles contain enough structure for the
    Strategy Engine to process the dataframe.

    This is NOT intended to force a trading signal.
    """

    rows = []

    price = 100.0

    for i in range(candles):

        open_price = price

        # Gradual movement with occasional larger candles.
        if i < candles - 10:

            high = price + 4.0
            low = price - 4.0
            close = price + 1.0

        else:

            high = price + 5.0
            low = price - 3.0
            close = price + 2.0

        rows.append(
            {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1000.0,
            }
        )

        price = close

    return pd.DataFrame(rows)


# ============================================================
# MARKET PACKAGE
# ============================================================

def create_market_data() -> dict:
    """
    Build the same market-data structure expected by
    evaluate_symbol().
    """

    daily = create_daily_data()

    h4 = create_h4_data()

    return {
        "1d": daily,
        "4h": h4,
    }


# ============================================================
# DISPLAY
# ============================================================

def display_signal(
    signal,
) -> None:

    print()
    print("STRATEGY ENGINE RESULT")
    print("-" * 60)

    if signal is None:

        print("Signal      : None")

        return

    print(
        f"Symbol      : {signal.get('symbol')}"
    )

    print(
        f"Pair        : {signal.get('pair')}"
    )

    print(
        f"Direction   : {signal.get('direction')}"
    )

    print(
        f"Side        : {signal.get('side')}"
    )

    print(
        f"Setup       : {signal.get('setup')}"
    )

    print(
        f"Entry Type  : {signal.get('entry_type')}"
    )

    print(
        f"Entry       : {signal.get('entry')}"
    )

    print(
        f"Confidence  : {signal.get('confidence')}"
    )

    print(
        f"Current     : {signal.get('current_price')}"
    )

    print(
        f"Status      : {signal.get('status')}"
    )

    print(
        f"Valid       : {signal.get('valid')}"
    )

    print(
        f"Entry Data  : {signal.get('entry_data')}"
    )


# ============================================================
# VALID SIGNAL STRUCTURE
# ============================================================

def validate_signal_structure(
    signal,
) -> bool:
    """
    Verify the minimum structure returned by the Strategy
    Engine when a signal exists.
    """

    if not isinstance(
        signal,
        dict,
    ):

        return False

    required = (
        "symbol",
        "pair",
        "direction",
        "side",
        "setup",
        "entry_type",
        "entry",
        "confidence",
        "current_price",
        "status",
        "valid",
    )

    for key in required:

        if key not in signal:

            print(
                f"Missing field: {key}"
            )

            return False

    if signal["direction"] not in (
        "BUY",
        "SELL",
    ):

        print(
            "Invalid direction."
        )

        return False

    if signal["side"] != signal["direction"]:

        print(
            "Side does not match direction."
        )

        return False

    if signal["valid"] is not True:

        print(
            "Signal valid flag is not True."
        )

        return False

    return True


# ============================================================
# TEST MARKET DATA
# ============================================================

def test_market_data(
    market: dict,
) -> bool:

    print()
    print("=" * 70)
    print("[1] MARKET DATA")
    print("=" * 70)

    if not isinstance(
        market,
        dict,
    ):

        print(
            "RESULT: MARKET DATA INVALID"
        )

        return False

    if "1d" not in market:

        print(
            "Missing Daily market data."
        )

        return False

    if "4h" not in market:

        print(
            "Missing H4 market data."
        )

        return False

    daily = market["1d"]

    h4 = market["4h"]

    print(
        f"Daily candles : {len(daily)}"
    )

    print(
        f"H4 candles    : {len(h4)}"
    )

    if len(daily) < 50:

        print(
            "RESULT: DAILY DATA FAILED"
        )

        return False

    if len(h4) < 100:

        print(
            "RESULT: H4 DATA FAILED"
        )

        return False

    print(
        f"Latest Daily close : {daily['close'].iloc[-1]}"
    )

    print(
        f"Latest H4 close    : {h4['close'].iloc[-1]}"
    )

    print(
        "RESULT: MARKET DATA SUCCESS"
    )

    return True


# ============================================================
# STRATEGY ENGINE TEST
# ============================================================

def test_strategy_engine(
    market: dict,
) -> bool:

    print()
    print("=" * 70)
    print("[2] STRATEGY ENGINE")
    print("=" * 70)

    try:

        signal = evaluate_symbol(
            symbol=SYMBOL,
            market_data=market,
        )

    except Exception as exc:

        print()
        print(
            "STRATEGY ENGINE EXCEPTION"
        )

        print(
            f"Error : {exc}"
        )

        traceback.print_exc()

        print()
        print(
            "RESULT: STRATEGY ENGINE FAILED"
        )

        return False

    display_signal(
        signal
    )

    # --------------------------------------------------------
    # NO SIGNAL IS VALID BEHAVIOR
    # --------------------------------------------------------

    if signal is None:

        print()
        print(
            "RESULT: NO SIGNAL — ENGINE CORRECTLY "
            "REJECTED TEST MARKET"
        )

        return True

    # --------------------------------------------------------
    # SIGNAL EXISTS
    # --------------------------------------------------------

    if not validate_signal_structure(
        signal
    ):

        print()
        print(
            "RESULT: SIGNAL STRUCTURE FAILED"
        )

        return False

    print()
    print(
        "RESULT: STRATEGY ENGINE SIGNAL SUCCESS"
    )

    return True


# ============================================================
# SIGNAL CONSISTENCY TEST
# ============================================================

def test_signal_consistency(
    market: dict,
) -> bool:

    print()
    print("=" * 70)
    print("[3] SIGNAL CONSISTENCY")
    print("=" * 70)

    try:

        signal_one = evaluate_symbol(
            symbol=SYMBOL,
            market_data=market,
        )

        signal_two = evaluate_symbol(
            symbol=SYMBOL,
            market_data=market,
        )

    except Exception as exc:

        print(
            f"ERROR: {exc}"
        )

        traceback.print_exc()

        return False

    # --------------------------------------------------------
    # BOTH NONE
    # --------------------------------------------------------

    if (
        signal_one is None
        and signal_two is None
    ):

        print(
            "Both evaluations correctly returned no signal."
        )

        print(
            "RESULT: CONSISTENCY SUCCESS"
        )

        return True

    # --------------------------------------------------------
    # ONE NONE / ONE SIGNAL
    # --------------------------------------------------------

    if (
        signal_one is None
        or signal_two is None
    ):

        print(
            "Inconsistent Strategy Engine result."
        )

        print(
            "RESULT: CONSISTENCY FAILED"
        )

        return False

    # --------------------------------------------------------
    # BOTH SIGNALS
    # --------------------------------------------------------

    fields = (
        "symbol",
        "direction",
        "setup",
        "entry_type",
        "entry",
        "confidence",
        "current_price",
    )

    for field in fields:

        if signal_one.get(field) != signal_two.get(field):

            print(
                f"Mismatch in field: {field}"
            )

            print(
                f"First : {signal_one.get(field)}"
            )

            print(
                f"Second: {signal_two.get(field)}"
            )

            print(
                "RESULT: CONSISTENCY FAILED"
            )

            return False

    print(
        "Repeated evaluation produced consistent results."
    )

    print(
        "RESULT: CONSISTENCY SUCCESS"
    )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "BLISSFINITY SIGNAL | STRATEGY ENGINE INTEGRATION TEST"
    )
    print("=" * 70)

    market = create_market_data()

    results = []

    # --------------------------------------------------------
    # MARKET DATA
    # --------------------------------------------------------

    results.append(
        test_market_data(
            market
        )
    )

    # --------------------------------------------------------
    # STRATEGY ENGINE
    # --------------------------------------------------------

    results.append(
        test_strategy_engine(
            market
        )
    )

    # --------------------------------------------------------
    # CONSISTENCY
    # --------------------------------------------------------

    results.append(
        test_signal_consistency(
            market
        )
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(
        1
        for result in results
        if result
    )

    total = len(results)

    print(
        f"Passed : {passed}/{total}"
    )

    if passed == total:

        print()
        print(
            "RESULT: ALL STRATEGY ENGINE TESTS PASSED"
        )

    else:

        print()
        print(
            "RESULT: SOME STRATEGY ENGINE TESTS FAILED"
        )

    print()
    print("=" * 70)
    print(
        "STRATEGY ENGINE INTEGRATION TEST COMPLETE"
    )
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()