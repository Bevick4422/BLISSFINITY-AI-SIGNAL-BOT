"""
BLISSFINITY SIGNAL
READ-ONLY PRODUCTION LIVE AUDIT
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol


def main() -> None:

    print()
    print("=" * 80)
    print("BLISSFINITY SIGNAL | READ-ONLY PRODUCTION LIVE AUDIT")
    print("=" * 80)

    signals = []
    no_signals = 0
    errors = 0

    print(f"Symbols configured : {len(SYMBOLS)}")
    print()

    for symbol in SYMBOLS:

        print("=" * 80)
        print(f"SCANNING: {symbol}")
        print("=" * 80)

        try:

            market_data = fetch_market_data(symbol)

            if market_data is None:
                print("RESULT: NO MARKET DATA")
                errors += 1
                continue

            signal = evaluate_symbol(
                symbol=symbol,
                market_data=market_data,
            )

            if signal is None:
                print("RESULT: NO SIGNAL")
                no_signals += 1
                continue

            signals.append(signal)

            print()
            print(">>> PRODUCTION SIGNAL DETECTED <<<")
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
            print(f"Status       : {signal.get('status')}")

        except Exception as exc:

            errors += 1

            print()
            print("RESULT: ENGINE ERROR")
            print(f"{type(exc).__name__}: {exc}")

    print()
    print("=" * 80)
    print("LIVE AUDIT SUMMARY")
    print("=" * 80)

    print(f"Signals found : {len(signals)}")
    print(f"No signals    : {no_signals}")
    print(f"Errors        : {errors}")

    if signals:

        print()
        print("SIGNALS")
        print("-" * 80)

        for signal in signals:

            print(
                f"{signal.get('symbol')} | "
                f"{signal.get('direction')} | "
                f"{signal.get('setup')} | "
                f"Entry={signal.get('entry')} | "
                f"SL={signal.get('stop_loss')} | "
                f"TP1={signal.get('tp1')} | "
                f"TP2={signal.get('tp2')}"
            )

    print()
    print("=" * 80)
    print("READ-ONLY LIVE AUDIT COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
