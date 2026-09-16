"""
BLISSFINITY SIGNAL
LIVE DAILY ENGULFING A/V AUDIT
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


async def audit_symbol(symbol):

    try:

        # fetch_market_data() is synchronous.
        market_data = fetch_market_data(symbol)

        if not market_data:
            return {
                "symbol": symbol,
                "status": "NO_DATA",
            }

        daily = market_data.get("1d")

        if daily is None or len(daily) < 3:
            return {
                "symbol": symbol,
                "status": "INSUFFICIENT_DAILY_DATA",
            }

        daily = get_completed_candles(
            daily,
            "1d",
        )

        if len(daily) < 3:
            return {
                "symbol": symbol,
                "status": "INSUFFICIENT_COMPLETED_DAILY",
            }

        engulfing = _find_daily_engulfing(daily)

        if engulfing is None:
            return {
                "symbol": symbol,
                "status": "NO_ENGULFING",
            }

        levels = _find_latest_va_levels(daily)

        conflict = _check_engulfing_level_conflict(
            daily,
            engulfing,
        )

        return {
            "symbol": symbol,
            "status": "ENGULFING",
            "direction": engulfing.get("direction"),
            "setup": engulfing.get("setup"),
            "setup_index": engulfing.get("setup_candle_index"),

            "latest_A": (
                levels["A_SHAPE"]["level"]
                if levels.get("A_SHAPE")
                else None
            ),

            "latest_A_index": (
                levels["A_SHAPE"]["level_index"]
                if levels.get("A_SHAPE")
                else None
            ),

            "latest_V": (
                levels["V_SHAPE"]["level"]
                if levels.get("V_SHAPE")
                else None
            ),

            "latest_V_index": (
                levels["V_SHAPE"]["level_index"]
                if levels.get("V_SHAPE")
                else None
            ),

            "selected_level": conflict.get("level"),
            "selected_level_index": conflict.get("level_index"),
            "interacts": conflict.get("interacts"),
            "rejection_conflict": conflict.get("conflict"),
            "reason": conflict.get("reason"),
        }

    except Exception as exc:

        return {
            "symbol": symbol,
            "status": "ERROR",
            "error": f"{type(exc).__name__}: {exc}",
        }


async def main():

    print("=" * 100)
    print("BLISSFINITY SIGNAL — LIVE DAILY ENGULFING A/V AUDIT")
    print("=" * 100)
    print()

    results = []

    for symbol in SYMBOLS:

        result = await audit_symbol(symbol)

        results.append(result)

        if result["status"] == "ENGULFING":

            print(
                f"{symbol} | "
                f"{result['direction']} | "
                f"{result['setup']} | "
                f"LEVEL={result['selected_level']} | "
                f"LEVEL_INDEX={result['selected_level_index']} | "
                f"INTERACTS={result['interacts']} | "
                f"CONFLICT={result['rejection_conflict']} | "
                f"{result['reason']}"
            )

        elif result["status"] == "ERROR":

            print(
                f"{symbol} | ERROR | {result['error']}"
            )

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)

    engulfings = [
        r for r in results
        if r["status"] == "ENGULFING"
    ]

    interacting = [
        r for r in engulfings
        if r["interacts"] is True
    ]

    non_interacting = [
        r for r in engulfings
        if r["interacts"] is False
    ]

    conflicts = [
        r for r in engulfings
        if r["rejection_conflict"] is True
    ]

    errors = [
        r for r in results
        if r["status"] == "ERROR"
    ]

    print(f"TOTAL SYMBOLS:        {len(results)}")
    print(f"DAILY ENGULFINGS:     {len(engulfings)}")
    print(f"A/V INTERACTIONS:     {len(interacting)}")
    print(f"NO A/V INTERACTION:   {len(non_interacting)}")
    print(f"REJECTION CONFLICTS:  {len(conflicts)}")
    print(f"ERRORS:               {len(errors)}")

    print()

    print("INTERACTION CHECK:")

    if non_interacting:
        print("FAIL")
    else:
        print("PASS")

    print()

    print("CONFLICT CHECK:")

    if conflicts:
        print("FAIL")
    else:
        print("PASS")

    print()
    print("=" * 100)
    print("END OF READ-ONLY AUDIT")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
