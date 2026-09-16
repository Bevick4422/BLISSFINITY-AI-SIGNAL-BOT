"""
BLISSFINITY SIGNAL
LIVE 5-SIGNAL PRODUCTION AUDIT

READ-ONLY.

Purpose:
1. Fetch LIVE MEXC market data.
2. Run the CURRENT production strategy_engine.evaluate_symbol().
3. Collect the first 5 genuine production signals.
4. Inspect the actual signal details.

IMPORTANT:
- Does NOT call record_signal()
- Does NOT call send_signal()
- Does NOT modify the database
- Does NOT modify production strategy files
- Does NOT change MAX_DAILY_SIGNALS
- Does NOT use the legacy signal engine
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol


MAX_LIVE_SIGNALS_TO_COLLECT = 5


def print_signal(number: int, signal: dict, engine_output: str) -> None:
    print()
    print("=" * 90)
    print(f"LIVE PRODUCTION SIGNAL #{number}")
    print("=" * 90)

    print(f"Symbol       : {signal.get('symbol')}")
    print(f"Direction    : {signal.get('direction')}")
    print(f"Setup        : {signal.get('setup')}")
    print(f"Entry Type   : {signal.get('entry_type')}")
    print(f"Entry        : {signal.get('entry')}")
    print(f"Stop Loss    : {signal.get('stop_loss')}")
    print(f"TP1          : {signal.get('tp1')}")
    print(f"TP2          : {signal.get('tp2')}")
    print(f"Risk         : {signal.get('risk')}")
    print(f"RR           : {signal.get('rr')}")
    print(f"Confidence   : {signal.get('confidence')}")
    print(f"Valid        : {signal.get('valid')}")
    print(f"Status       : {signal.get('status')}")

    print()
    print("-" * 90)
    print("STRATEGY ENGINE TRACE")
    print("-" * 90)

    if engine_output.strip():
        print(engine_output.strip())
    else:
        print("No diagnostic output captured.")

    print("=" * 90)


def main() -> None:
    print("=" * 90)
    print("BLISSFINITY SIGNAL — LIVE 5-SIGNAL PRODUCTION AUDIT")
    print("=" * 90)
    print()
    print("READ-ONLY TEST")
    print("No trades will be recorded.")
    print("No Telegram/Discord notifications will be sent.")
    print()

    signals = []
    errors = 0
    scanned = 0

    for symbol in SYMBOLS:
        if len(signals) >= MAX_LIVE_SIGNALS_TO_COLLECT:
            break

        scanned += 1

        print(
            f"[{scanned}/{len(SYMBOLS)}] "
            f"Scanning {symbol}...",
            end=" ",
            flush=True,
        )

        try:
            market_data = fetch_market_data(symbol)

            if not market_data:
                print("NO DATA")
                continue

            # ---------------------------------------------------------
            # RUN THE REAL PRODUCTION STRATEGY ENGINE
            # ---------------------------------------------------------

            captured_output = io.StringIO()

            with redirect_stdout(captured_output):
                signal = evaluate_symbol(
                    symbol=symbol,
                    market_data=market_data,
                )

            engine_output = captured_output.getvalue()

            if signal is None:
                print("NO SIGNAL")
                continue

            signals.append(signal)

            print(
                f"SIGNAL FOUND | "
                f"{signal.get('direction')} | "
                f"{signal.get('setup')}"
            )

            print_signal(
                len(signals),
                signal,
                engine_output,
            )

        except Exception as exc:
            errors += 1

            print(
                f"ERROR | "
                f"{type(exc).__name__}: {exc}"
            )

    # -------------------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------------------

    print()
    print("=" * 90)
    print("LIVE 5-SIGNAL AUDIT SUMMARY")
    print("=" * 90)

    print(f"Symbols Scanned : {scanned}")
    print(f"Signals Found   : {len(signals)}")
    print(f"Errors          : {errors}")
    print()

    if signals:
        print("SIGNALS COLLECTED")
        print("-" * 90)

        for i, signal in enumerate(signals, 1):
            print(
                f"{i}. "
                f"{signal.get('symbol')} | "
                f"{signal.get('direction')} | "
                f"{signal.get('setup')} | "
                f"Entry={signal.get('entry')} | "
                f"SL={signal.get('stop_loss')} | "
                f"TP1={signal.get('tp1')} | "
                f"TP2={signal.get('tp2')} | "
                f"RR={signal.get('rr')} | "
                f"Valid={signal.get('valid')} | "
                f"Status={signal.get('status')}"
            )

    print()
    print("=" * 90)

    if len(signals) == MAX_LIVE_SIGNALS_TO_COLLECT:
        print("RESULT: 5 LIVE PRODUCTION SIGNALS COLLECTED")
    elif len(signals) > 0:
        print(
            f"RESULT: ONLY {len(signals)} LIVE SIGNAL(S) "
            f"FOUND BEFORE SYMBOL LIST ENDED"
        )
    else:
        print("RESULT: NO LIVE PRODUCTION SIGNALS FOUND")

    if errors:
        print(f"WARNING: {errors} SYMBOL(S) PRODUCED ERRORS")

    print("=" * 90)
    print()
    print("READ-ONLY AUDIT COMPLETE")


if __name__ == "__main__":
    main()
