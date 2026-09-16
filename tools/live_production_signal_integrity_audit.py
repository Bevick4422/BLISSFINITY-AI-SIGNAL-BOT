"""
BLISSFINITY SIGNAL
LIVE PRODUCTION SIGNAL INTEGRITY AUDIT

READ-ONLY

Verifies:
Daily -> Strategy -> Production Signal
without recording trades or sending Telegram.
"""

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol
from signal_engine.signal_builder import validate_signal


def check_signal(signal):

    if not signal:
        return {
            "valid": False,
            "reason": "NO_SIGNAL",
        }

    required = (
        "symbol",
        "direction",
        "setup",
        "entry_type",
        "entry",
        "stop_loss",
        "tp1",
        "tp2",
        "risk",
        "reward",
        "rr",
        "confidence",
    )

    missing = [
        field
        for field in required
        if field not in signal
    ]

    if missing:
        return {
            "valid": False,
            "reason": f"MISSING_FIELDS: {missing}",
        }

    direction = signal["direction"]

    entry = float(signal["entry"])
    stop = float(signal["stop_loss"])
    tp1 = float(signal["tp1"])
    tp2 = float(signal["tp2"])

    risk = abs(entry - stop)

    expected_tp1 = (
        entry + risk * 2
        if direction == "BUY"
        else entry - risk * 2
    )

    expected_tp2 = (
        entry + risk * 3
        if direction == "BUY"
        else entry - risk * 3
    )

    tolerance = max(abs(entry) * 1e-8, 1e-12)

    if direction == "BUY":

        if stop >= entry:
            return {
                "valid": False,
                "reason": "BUY_STOP_NOT_BELOW_ENTRY",
            }

        if tp1 <= entry:
            return {
                "valid": False,
                "reason": "BUY_TP1_NOT_ABOVE_ENTRY",
            }

        if tp2 <= tp1:
            return {
                "valid": False,
                "reason": "BUY_TP2_NOT_ABOVE_TP1",
            }

    elif direction == "SELL":

        if stop <= entry:
            return {
                "valid": False,
                "reason": "SELL_STOP_NOT_ABOVE_ENTRY",
            }

        if tp1 >= entry:
            return {
                "valid": False,
                "reason": "SELL_TP1_NOT_BELOW_ENTRY",
            }

        if tp2 >= tp1:
            return {
                "valid": False,
                "reason": "SELL_TP2_NOT_BELOW_TP1",
            }

    else:

        return {
            "valid": False,
            "reason": f"INVALID_DIRECTION: {direction}",
        }

    if abs(tp1 - expected_tp1) > tolerance:
        return {
            "valid": False,
            "reason": (
                f"TP1_NOT_2R: "
                f"actual={tp1} expected={expected_tp1}"
            ),
        }

    if abs(tp2 - expected_tp2) > tolerance:
        return {
            "valid": False,
            "reason": (
                f"TP2_NOT_3R: "
                f"actual={tp2} expected={expected_tp2}"
            ),
        }

    try:

        validation = validate_signal(signal)

        if validation is False:
            return {
                "valid": False,
                "reason": "PRODUCTION_VALIDATOR_REJECTED",
            }

    except Exception as exc:

        return {
            "valid": False,
            "reason": (
                f"VALIDATOR_ERROR: "
                f"{type(exc).__name__}: {exc}"
            ),
        }

    return {
        "valid": True,
        "reason": "VALID",
    }


async def main():

    print("=" * 110)
    print("BLISSFINITY SIGNAL — LIVE PRODUCTION SIGNAL INTEGRITY AUDIT")
    print("=" * 110)
    print()

    total_symbols = 0
    signals = 0
    valid = 0
    invalid = 0
    errors = 0

    for symbol in SYMBOLS:

        total_symbols += 1

        try:

            market_data = fetch_market_data(symbol)

            if not market_data:
                continue

            signal = evaluate_symbol(
                symbol=symbol,
                market_data=market_data,
            )

            if not signal:
                continue

            signals += 1

            result = check_signal(signal)

            if result["valid"]:

                valid += 1

                print(
                    f"{symbol} | "
                    f"{signal['direction']} | "
                    f"{signal['setup']} | "
                    f"ENTRY={signal['entry']} | "
                    f"SL={signal['stop_loss']} | "
                    f"TP1={signal['tp1']} | "
                    f"TP2={signal['tp2']} | "
                    f"RR={signal['rr']} | "
                    f"VALID=True"
                )

            else:

                invalid += 1

                print(
                    f"{symbol} | INVALID | "
                    f"{result['reason']}"
                )

        except Exception as exc:

            errors += 1

            print(
                f"{symbol} | ERROR | "
                f"{type(exc).__name__}: {exc}"
            )

    print()
    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)

    print(f"TOTAL SYMBOLS:       {total_symbols}")
    print(f"PRODUCTION SIGNALS:  {signals}")
    print(f"VALID SIGNALS:       {valid}")
    print(f"INVALID SIGNALS:     {invalid}")
    print(f"ERRORS:              {errors}")

    print()
    print("=" * 110)

    if errors:
        print("RESULT: FAIL — SIGNAL PIPELINE ERRORS")

    elif invalid:
        print("RESULT: FAIL — INVALID PRODUCTION SIGNALS FOUND")

    else:
        print(
            "RESULT: PASS — "
            "ALL LIVE PRODUCTION SIGNALS PASSED INTEGRITY CHECK"
        )

    print("=" * 110)


if __name__ == "__main__":
    asyncio.run(main())
