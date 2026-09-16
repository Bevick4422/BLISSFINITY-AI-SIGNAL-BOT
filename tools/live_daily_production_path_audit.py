"""
BLISSFINITY SIGNAL
LIVE DAILY -> PRODUCTION PATH AUDIT

READ-ONLY DIAGNOSTIC
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from analysis.candle_gate import get_completed_candles

from analysis.daily_structure.daily_structure_engine import (
    _find_daily_engulfing,
    _find_latest_va_levels,
    _check_engulfing_level_conflict,
)

from engine.strategy_engine import evaluate_symbol


async def audit_symbol(symbol):

    try:

        market_data = fetch_market_data(symbol)

        if not market_data:
            return {
                "symbol": symbol,
                "status": "NO_DATA",
            }

        daily = market_data.get("1d")
        h4 = market_data.get("4h")

        if daily is None or h4 is None:
            return {
                "symbol": symbol,
                "status": "MISSING_DATA",
            }

        daily = get_completed_candles(daily, "1d")
        h4 = get_completed_candles(h4, "4h")

        if len(daily) < 3 or len(h4) < 3:
            return {
                "symbol": symbol,
                "status": "INSUFFICIENT_DATA",
            }

        # ---------------------------------------------------------
        # RAW DAILY ENGULFING
        # ---------------------------------------------------------

        engulfing = _find_daily_engulfing(daily)

        # ---------------------------------------------------------
        # PRODUCTION STRATEGY ENGINE
        #
        # IMPORTANT:
        # Production API accepts the complete market_data dict.
        # ---------------------------------------------------------

        production = evaluate_symbol(
            symbol=symbol,
            market_data={
                "1d": daily,
                "4h": h4,
            },
        )

        # ---------------------------------------------------------
        # NO RAW ENGULFING
        # ---------------------------------------------------------

        if engulfing is None:

            return {
                "symbol": symbol,
                "status": "NO_ENGULFING",
            }

        # ---------------------------------------------------------
        # DAILY A/V GATE
        # ---------------------------------------------------------

        levels = _find_latest_va_levels(daily)

        conflict = _check_engulfing_level_conflict(
            daily,
            engulfing,
        )

        interacts = conflict.get("interacts")
        rejection = conflict.get("conflict")

        # ---------------------------------------------------------
        # EXPECTED PRODUCTION RESULT
        # ---------------------------------------------------------

        if not interacts:
            expected = "NO_SIGNAL"

        elif rejection:
            expected = "NO_SIGNAL"

        else:
            expected = engulfing.get("direction")

        # ---------------------------------------------------------
        # ACTUAL PRODUCTION RESULT
        # ---------------------------------------------------------

        if production:

            actual = production.get("direction")
            actual_setup = production.get("setup")

        else:

            actual = "NO_SIGNAL"
            actual_setup = None

        # ---------------------------------------------------------
        # COMPARE
        # ---------------------------------------------------------

        passed = actual == expected

        return {
            "symbol": symbol,

            "status": "ENGULFING",

            "raw_direction": engulfing.get("direction"),
            "raw_setup": engulfing.get("setup"),

            "latest_A": (
                levels["A_SHAPE"]["level"]
                if levels.get("A_SHAPE")
                else None
            ),

            "latest_V": (
                levels["V_SHAPE"]["level"]
                if levels.get("V_SHAPE")
                else None
            ),

            "selected_level": conflict.get("level"),
            "selected_level_index": conflict.get("level_index"),

            "interacts": interacts,
            "rejection_conflict": rejection,

            "gate_reason": conflict.get("reason"),

            "expected": expected,

            "actual": actual,
            "actual_setup": actual_setup,

            "passed": passed,
        }

    except Exception as exc:

        return {
            "symbol": symbol,
            "status": "ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }


async def main():

    print("=" * 115)
    print("BLISSFINITY SIGNAL — DAILY → PRODUCTION PATH AUDIT")
    print("=" * 115)
    print()

    results = []

    for symbol in SYMBOLS:

        result = await audit_symbol(symbol)

        results.append(result)

        if result["status"] == "ENGULFING":

            print(
                f"{symbol} | "
                f"RAW={result['raw_direction']} | "
                f"INTERACTS={result['interacts']} | "
                f"CONFLICT={result['rejection_conflict']} | "
                f"EXPECTED={result['expected']} | "
                f"ACTUAL={result['actual']} | "
                f"PASS={result['passed']}"
            )

        elif result["status"] == "ERROR":

            print(
                f"{symbol} | "
                f"ERROR | "
                f"{result['error']}"
            )

    print()
    print("=" * 115)
    print("SUMMARY")
    print("=" * 115)

    engulfings = [
        r for r in results
        if r["status"] == "ENGULFING"
    ]

    passed = [
        r for r in engulfings
        if r["passed"] is True
    ]

    failed = [
        r for r in engulfings
        if r["passed"] is False
    ]

    errors = [
        r for r in results
        if r["status"] == "ERROR"
    ]

    expected_signals = [
        r for r in engulfings
        if r["expected"] != "NO_SIGNAL"
    ]

    expected_rejections = [
        r for r in engulfings
        if r["expected"] == "NO_SIGNAL"
    ]

    print(f"TOTAL SYMBOLS:          {len(results)}")
    print(f"DAILY ENGULFINGS:       {len(engulfings)}")
    print(f"EXPECTED SIGNALS:       {len(expected_signals)}")
    print(f"EXPECTED NO SIGNAL:     {len(expected_rejections)}")
    print(f"PRODUCTION PATH PASSED: {len(passed)}")
    print(f"PRODUCTION PATH FAILED: {len(failed)}")
    print(f"ERRORS:                  {len(errors)}")

    print()

    if failed:

        print("FAILED CASES")
        print("-" * 115)

        for r in failed:

            print(
                f"{r['symbol']} | "
                f"RAW={r['raw_direction']} | "
                f"INTERACTS={r['interacts']} | "
                f"CONFLICT={r['rejection_conflict']} | "
                f"EXPECTED={r['expected']} | "
                f"ACTUAL={r['actual']} | "
                f"REASON={r['gate_reason']}"
            )

    print()
    print("=" * 115)

    if errors:

        print("RESULT: FAIL — DIAGNOSTIC/PRODUCTION EXECUTION ERRORS")

    elif failed:

        print("RESULT: FAIL — DAILY GATE AND PRODUCTION ENGINE DISAGREE")

    else:

        print(
            "RESULT: PASS — "
            "DAILY GATE IS RESPECTED BY PRODUCTION PATH"
        )

    print("=" * 115)
    print()
    print("END OF READ-ONLY AUDIT")


if __name__ == "__main__":
    asyncio.run(main())
