
from data.mexc_api import fetch_ohlcv

from signals.ai_signal_engine import generate_signal
from signals.smart_risk_manager import apply_smart_risk
from signals.telegram_formatter import format_signal

# Uncomment after telegram sender is finished
# from telegram.telegram_sender import send_signal

TIMEFRAME = "4h"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "XRPUSDT",
]


def scan_market():

    for symbol in SYMBOLS:

        try:

            df = fetch_ohlcv(
                symbol=symbol,
                timeframe=TIMEFRAME,
                limit=500,
            )

            if df is None or len(df) < 100:
                continue

            signal = generate_signal(df, symbol)

            if signal is None:
                continue

            signal = apply_smart_risk(signal)

            message = format_signal(signal)

            print(message)

            # Enable after Telegram sender works
            # send_signal(message)

        except Exception as e:
            print(f"{symbol}: {e}")
