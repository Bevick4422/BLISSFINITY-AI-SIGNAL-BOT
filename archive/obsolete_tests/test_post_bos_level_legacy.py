from market_data.fetcher import fetch_ohlcv
from analysis.h4_bos.h4_bos_engine import detect_h4_bos
from analysis.entry.post_bos_level import detect_post_bos_level


SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
]

H4_LIMIT = 300


def test_symbol(symbol):
    print("\n" + "=" * 60)
    print(f"TESTING {symbol}")
    print("=" * 60)

    h4_df = fetch_ohlcv(
        symbol=symbol,
        timeframe="4h",
        limit=H4_LIMIT,
    )

    if h4_df is None or h4_df.empty:
        print("H4 data unavailable")
        return

    print(f"H4 candles: {len(h4_df)}")

    bos_result = detect_h4_bos(h4_df)

    print("\nH4 BOS:")
    print(bos_result)

    if not bos_result.get("bos"):
        print("\nNo current H4 BOS found")
        return

    direction = bos_result.get("direction")
    bos_index = bos_result.get("break_index")

    print(f"\nBOS direction: {direction}")
    print(f"BOS timestamp: {bos_index}")

    result = detect_post_bos_level(
        df=h4_df,
        bos_index=bos_index,
        direction=direction,
    )

    print("\nPOST-BOS LEVEL RESULT:")
    print(result)

    if result.get("valid"):
        print("\nVALID POST-BOS LEVEL FOUND")
        print(f"Entry: {result.get('entry')}")
        print(f"Level index: {result.get('level_index')}")
    else:
        print("\nNo valid post-BOS level found")


def main():
    for symbol in SYMBOLS:
        try:
            test_symbol(symbol)

        except Exception as exc:
            print(
                f"\nERROR testing {symbol}: "
                f"{type(exc).__name__}: {exc}"
            )


if __name__ == "__main__":
    main()