import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol


print()
print("=" * 130)
print("BLISSFINITY LIVE SIGNAL QUALITY INSPECTION")
print("=" * 130)
print()

print(
    f"{'SYMBOL':<22}"
    f"{'DIR':<7}"
    f"{'SETUP':<22}"
    f"{'ENTRY':<14}"
    f"{'CURRENT':<14}"
    f"{'SL':<14}"
    f"{'TP1':<14}"
    f"{'TP2':<14}"
    f"{'RR':<8}"
    f"{'CONF':<8}"
)

print("-" * 130)

signal_count = 0

for symbol in SYMBOLS:

    try:
        market_data = fetch_market_data(symbol)
        signal = evaluate_symbol(symbol, market_data)

        if not signal:
            continue

        signal_count += 1

        print(
            f"{symbol:<22}"
            f"{str(signal.get('direction')):<7}"
            f"{str(signal.get('setup')):<22}"
            f"{str(signal.get('entry')):<14}"
            f"{str(signal.get('current_price')):<14}"
            f"{str(signal.get('stop_loss')):<14}"
            f"{str(signal.get('tp1')):<14}"
            f"{str(signal.get('tp2')):<14}"
            f"{str(signal.get('rr')):<8}"
            f"{str(signal.get('confidence')):<8}"
        )

    except Exception as exc:
        print(f"{symbol:<22} ERROR: {exc}")


print()
print("=" * 130)
print(f"TOTAL PRODUCTION SIGNALS: {signal_count}")
print("=" * 130)