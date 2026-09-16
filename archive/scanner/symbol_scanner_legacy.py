
"""
BLISSFINITY AI SIGNAL BOT
SYMBOL SCANNER
"""

import traceback

from config.settings import (
    SYMBOLS,
    MAX_PAIRS,
)

from market_data.fetcher import fetch_market_data
from engine.strategy_engine import evaluate_symbol


def scan_symbol(symbol):
    """
    Scan a single trading pair.
    """

    try:

        market = fetch_market_data(symbol)

        if market is None:
            return None

        signal = evaluate_symbol(
    symbol,
    market,
)

        return signal

    except Exception as e:

        print(f"{symbol} Scan Error: {e}")
        traceback.print_exc()

        return None


def scan_market():
    """
    Scan all configured symbols.
    """

    signals = []

    symbols = SYMBOLS[:MAX_PAIRS]

    print(f"\nScanning {len(symbols)} markets...\n")

    for symbol in symbols:

        signal = scan_symbol(symbol)

        if signal:

            signals.append(signal)

            print(f"✓ Signal detected: {symbol}")

        else:

            print(f"• No signal generated yet: {symbol}")

    return signals

if __name__ == "__main__":

    results = scan_market()

    print("\n============================")
    print(f"Signals Found : {len(results)}")
    print("============================")

    for signal in results:
        print(signal)