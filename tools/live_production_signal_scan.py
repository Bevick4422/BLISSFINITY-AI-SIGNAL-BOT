from pathlib import Path
import sys

# ------------------------------------------------------------
# PROJECT ROOT
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ------------------------------------------------------------
# PRODUCTION IMPORTS
# ------------------------------------------------------------

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol


# ------------------------------------------------------------
# LIVE READ-ONLY SCAN
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("BLISSFINITY LIVE PRODUCTION SIGNAL SCAN")
print("READ-ONLY | NO TELEGRAM | NO TRADE RECORDING")
print("=" * 80)

signals = []
errors = []
no_signal = 0

print(f"\nTOTAL SYMBOLS: {len(SYMBOLS)}\n")

for i, symbol in enumerate(SYMBOLS, 1):

    try:
        print(
            f"[{i}/{len(SYMBOLS)}] {symbol} ...",
            end=" ",
            flush=True,
        )

        market_data = fetch_market_data(symbol)

        if market_data is None:
            print("NO DATA")
            errors.append((symbol, "NO DATA"))
            continue

        signal = evaluate_symbol(
            symbol=symbol,
            market_data=market_data,
        )

        if not signal:
            print("NO SIGNAL")
            no_signal += 1
            continue

        signals.append(signal)

        print(
            f"SIGNAL | "
            f"{signal.get('direction')} | "
            f"{signal.get('setup')} | "
            f"Entry={signal.get('entry')} | "
            f"SL={signal.get('stop_loss')} | "
            f"TP1={signal.get('tp1')} | "
            f"TP2={signal.get('tp2')} | "
            f"RR={signal.get('rr')}"
        )

    except Exception as exc:
        print(f"ERROR: {exc}")
        errors.append((symbol, str(exc)))


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("LIVE PRODUCTION SCAN SUMMARY")
print("=" * 80)

print(f"Total symbols : {len(SYMBOLS)}")
print(f"Signals       : {len(signals)}")
print(f"No signal     : {no_signal}")
print(f"Errors        : {len(errors)}")


# ------------------------------------------------------------
# SIGNAL DETAILS
# ------------------------------------------------------------

if signals:

    print("\n" + "-" * 80)
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
            f"TP2={signal.get('tp2')} | "
            f"RR={signal.get('rr')} | "
            f"Confidence={signal.get('confidence')}"
        )


# ------------------------------------------------------------
# ERRORS
# ------------------------------------------------------------

if errors:

    print("\n" + "-" * 80)
    print("ERRORS")
    print("-" * 80)

    for symbol, error in errors:
        print(f"{symbol} | {error}")


print("\n" + "=" * 80)
print("SCAN COMPLETE")
print("=" * 80)
