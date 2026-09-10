from market_data.fetcher import fetch_ohlcv
from analysis.daily_setup.daily_engine import detect_daily_setup
from analysis.h4_bos.h4_bos_engine import detect_h4_bos
from analysis.entry.entry_selector import select_best_entry


SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
]

DAILY_LIMIT = 300
H4_LIMIT = 300


# ==========================================================
# DAILY → H4 TIMESTAMP MAPPING
# ==========================================================

def map_daily_index_to_h4(
    daily_df,
    h4_df,
    daily_level_index,
):
    """
    Convert the Daily setup candle position into
    the corresponding H4 positional index.
    """

    if daily_df is None or h4_df is None:
        return None

    if daily_level_index is None:
        return None

    try:
        daily_level_index = int(daily_level_index)

        if not 0 <= daily_level_index < len(daily_df):
            return None

        daily_timestamp = daily_df.index[daily_level_index]

        h4_position = h4_df.index.searchsorted(
            daily_timestamp,
            side="right",
        ) - 1

        if not 0 <= h4_position < len(h4_df):
            return None

        return int(h4_position)

    except (
        AttributeError,
        IndexError,
        TypeError,
        ValueError,
    ):
        return None


# ==========================================================
# INDEX DIAGNOSTIC
# ==========================================================

def print_index_diagnostic(
    daily_df,
    h4_df,
    daily_setup,
):
    print("\nINDEX DIAGNOSTIC")

    daily_level_index = daily_setup.get("level_index")

    print(f"Daily level index: {daily_level_index}")

    if daily_level_index is None:
        print("No Daily level index available")
        return None

    if not 0 <= daily_level_index < len(daily_df):
        print("Daily level index is outside Daily data")
        return None

    daily_timestamp = daily_df.index[daily_level_index]

    print(f"Daily creation candle: {daily_timestamp}")

    h4_level_index = map_daily_index_to_h4(
        daily_df=daily_df,
        h4_df=h4_df,
        daily_level_index=daily_level_index,
    )

    print(f"Mapped H4 level index: {h4_level_index}")

    if h4_level_index is None:
        print("Could not map Daily timestamp to H4 data")
        return None

    print(
        "Mapped H4 creation candle: "
        f"{h4_df.index[h4_level_index]}"
    )

    if 0 <= daily_level_index < len(h4_df):
        print(
            "H4 candle at same numeric index: "
            f"{h4_df.index[daily_level_index]}"
        )
    else:
        print("Daily index is outside H4 data")

    print(
        "Correct mapping uses timestamps, "
        "not the same numeric index."
    )

    return h4_level_index


# ==========================================================
# TEST SYMBOL
# ==========================================================

def test_symbol(symbol):
    print("\n" + "=" * 60)
    print(f"TESTING {symbol}")
    print("=" * 60)

    # ------------------------------------------------------
    # FETCH MARKET DATA
    # ------------------------------------------------------

    daily_df = fetch_ohlcv(
        symbol=symbol,
        timeframe="1d",
        limit=DAILY_LIMIT,
    )

    h4_df = fetch_ohlcv(
        symbol=symbol,
        timeframe="4h",
        limit=H4_LIMIT,
    )

    if daily_df is None or daily_df.empty:
        print("Daily data unavailable")
        return

    if h4_df is None or h4_df.empty:
        print("H4 data unavailable")
        return

    print(f"Daily candles: {len(daily_df)}")
    print(f"H4 candles: {len(h4_df)}")

    # ------------------------------------------------------
    # DAILY SETUP
    # ------------------------------------------------------

    daily_setup = detect_daily_setup(daily_df)

    print("\nDAILY SETUP:")
    print(daily_setup)

    if not isinstance(daily_setup, dict):
        print("\nInvalid Daily setup result")
        return

    if not daily_setup.get("valid"):
        print("\nNo valid Daily setup")
        return

    direction = daily_setup.get("direction")
    setup = daily_setup.get("setup")
    level = daily_setup.get("level")
    daily_level_index = daily_setup.get("level_index")
    daily_entry = daily_setup.get("entry")

    if direction not in ("BUY", "SELL"):
        print("\nInvalid Daily direction")
        return

    if level is None:
        print("\nDaily setup has no level")
        return

    h4_level_index = print_index_diagnostic(
        daily_df=daily_df,
        h4_df=h4_df,
        daily_setup=daily_setup,
    )

    if h4_level_index is None:
        print("\nCould not map Daily level to H4 index")
        return

    # ------------------------------------------------------
    # H4 BOS
    # ------------------------------------------------------

    print("\nH4 BOS:")

    bos_result = detect_h4_bos(h4_df)

    print(bos_result)

    if not isinstance(bos_result, dict):
        print("\nInvalid H4 BOS result")
        return

    if not bos_result.get("bos"):
        print("\nNo current H4 BOS found")
        return

    # IMPORTANT:
    # These variables must be outside the no-BOS return block.
    bos_direction = bos_result.get("direction")
    bos_level = bos_result.get("broken_level")
    bos_index = bos_result.get("break_index")

    print(f"H4 BOS direction: {bos_direction}")
    print(f"H4 broken level: {bos_level}")
    print(f"H4 BOS index: {bos_index}")

    if bos_direction != direction:
        print(
            "\nDirection mismatch: "
            f"Daily={direction}, "
            f"H4={bos_direction}"
        )
        return

    if bos_level is None:
        print("\nH4 BOS has no broken level")
        return

    if bos_index is None:
        print("\nH4 BOS has no break index")
        return

    # ------------------------------------------------------
    # ENTRY SELECTION
    # ------------------------------------------------------

    entry_result = select_best_entry(
        df=h4_df,
        level=level,
        direction=direction,

        # Correct H4 mapping of the Daily setup candle.
        level_index=h4_level_index,

        bos_level=bos_level,
        bos_index=bos_index,

        setup=setup,
        daily_entry=daily_entry,
    )

    print("\nENTRY RESULT:")
    print(entry_result)

    if not isinstance(entry_result, dict):
        print("\nInvalid entry result")
        return

    if not entry_result.get("valid"):
        print("\nNo valid entry found")
        return

    # ------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------

    print("\n" + "=" * 60)
    print("SUCCESS: COMPLETE SETUP FOUND")
    print("=" * 60)

    print(f"Symbol: {symbol}")
    print(f"Direction: {direction}")
    print(f"Setup: {setup}")
    print(f"Daily level: {level}")
    print(f"Daily level index: {daily_level_index}")
    print(f"H4 mapped level index: {h4_level_index}")
    print(f"H4 BOS index: {bos_index}")
    print(f"Entry result: {entry_result}")


# ==========================================================
# MAIN
# ==========================================================

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