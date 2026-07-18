from market_data.mexc_client import get_klines
from signals.ai_signal_engine import generate_signal

# Initial watchlist
from market_data.symbol_fetcher import get_all_symbols

SYMBOLS = get_all_symbols()    "BTC_USDT",
    "ETH_USDT",
    "SOL_USDT",
    "XRP_USDT",
    "BNB_USDT",
    "DOGE_USDT",
    "ADA_USDT",
    "LINK_USDT",
    "AVAX_USDT",
    "SUI_USDT",
]


def scan_market():

    print("=" * 50)
    print("BLISSFINITY MARKET SCANNER")
    print("=" * 50)

    signals = []

    for symbol in SYMBOLS:

        try:

            print(f"Scanning {symbol}...")

            df = get_klines(
                symbol=symbol,
                interval="15m",
                limit=300
            )

            signal = generate_signal(df)

            if signal:

                signal["pair"] = symbol
                signals.append(signal)

                print(f"✅ SIGNAL FOUND -> {symbol}")

        except Exception as e:

            print(f"❌ {symbol} -> {e}")

    print()

    print(f"Finished scanning.")

    print(f"Signals Found: {len(signals)}")

    return signals


if __name__ == "__main__":
    scan_market()
