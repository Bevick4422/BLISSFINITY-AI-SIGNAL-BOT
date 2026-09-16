
"""
BLISSFINITY AI SIGNAL BOT
MAIN
"""

import asyncio

from config.settings import (
    SYMBOLS,
    SCAN_INTERVAL,
    MAX_SIGNALS_PER_SCAN
)

from signal_engine import generate_signal

from telegram.sender import send_signal

from tracking.trade_manager import add_trade

from tracking.lifecycle.trade_monitor import monitor_trades


async def run():

    print("\n")
    print("=" * 60)
    print("      BLISSFINITY AI SIGNAL BOT")
    print("=" * 60)

    print(f"Pairs Loaded      : {len(SYMBOLS)}")
    print(f"Scan Interval     : {SCAN_INTERVAL} seconds")
    print(f"Max Signals/Scan  : {MAX_SIGNALS_PER_SCAN}")

    print("=" * 60)
    print()

    while True:

        print("\n========== NEW MARKET SCAN ==========\n")

        signals_sent = 0

        for symbol in SYMBOLS:

            if signals_sent >= MAX_SIGNALS_PER_SCAN:
                break

            signal = generate_signal(symbol)

            if signal is None:

                print(f"{symbol} | No Signal")

                continue

            if add_trade(signal):

                await send_signal(signal)

                signals_sent += 1

                print(f"{symbol} | SIGNAL SENT")

        await monitor_trades()

        print(f"\nNext scan in {SCAN_INTERVAL} seconds...")

        await asyncio.sleep(SCAN_INTERVAL)


if __name__ == "__main__":

    asyncio.run(run())