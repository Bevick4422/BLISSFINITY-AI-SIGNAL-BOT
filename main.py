
"""
BLISSFINITY AI SIGNAL BOT
MAIN ENTRY POINT
"""

import asyncio

from signal_engine import generate_signal
from telegram.sender import send_signal
from tracking.trade_manager import add_trade
from tracking.lifecycle.trade_monitor import monitor_trades

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT"
]


async def run():

    while True:

        print("\n========== NEW MARKET SCAN ==========\n")

        # Monitor existing trades
        try:
            await monitor_trades()
        except Exception as e:
            print(f"Trade Monitor Error: {e}")

        # Scan markets
        for symbol in SYMBOLS:

            try:

                signal = generate_signal(symbol)

                if signal is None:

                    print(f"{symbol} | No Signal")
                    continue

                if add_trade(signal):

                    await send_signal(signal)

                    print(f"{symbol} | Signal Sent")

                else:

                    print(f"{symbol} | Duplicate Signal")

            except Exception as e:

                print(f"{symbol} | ERROR -> {e}")

        print("\nNext scan in 60 seconds...\n")

        await asyncio.sleep(60)


if __name__ == "__main__":

    asyncio.run(run())