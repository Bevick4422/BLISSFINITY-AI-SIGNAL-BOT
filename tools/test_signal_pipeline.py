import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market_data.fetcher import fetch_market_data
from analysis.daily_setup.daily_engine import detect_daily_setup
from analysis.h4_bos.h4_bos_engine import detect_h4_bos
from analysis.entry.entry_selector import select_best_entry
from engine.signal_builder import build_signal


SYMBOLS = [
    "BTC/USDT:USDT",
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
]


def display_signal(signal):
    if not signal:
        print("RESULT: INVALID SIGNAL")
        return

    print("RESULT: VALID SIGNAL")
    print(f"Symbol: {signal.get('symbol')}")
    print(f"Direction: {signal.get('direction')}")
    print(f"Setup: {signal.get('setup')}")
    print(f"Entry: {signal.get('entry')}")
    print(f"Stop Loss: {signal.get('stop_loss')}")
    print(f"Take Profit: {signal.get('take_profit')}")
    print(f"Risk/Reward: {signal.get('risk_reward')}")
    print(f"Confidence: {signal.get('confidence')}")


def build_and_display_signal(
    symbol,
    direction,
    setup,
    candle_data,
    market_data,
    entry,
    entry_type,
):
    signal = build_signal(
        symbol=symbol,
        direction=direction,
        setup=setup,
        candle_data=candle_data,
        entry=entry,
        entry_type=entry_type,
        market_data=market_data,
    )

    display_signal(signal)


def test_symbol(symbol):
    print("\n" + "=" * 70)
    print(f"TESTING: {symbol}")
    print("=" * 70)

    try:
        market_data = fetch_market_data(symbol)

        if market_data is None:
            print("Market data unavailable")
            return

        daily = market_data.get("1d")

        trend_keys = [
            key for key in market_data.keys()
            if key != "1d"
        ]

        if not trend_keys:
            print("Trend data unavailable")
            return

        h4 = market_data[trend_keys[0]]

        if daily is None or daily.empty:
            print("Daily data unavailable")
            return

        if h4 is None or h4.empty:
            print("Trend data unavailable")
            return

        print(f"Daily candles: {len(daily)}")
        print(f"Trend candles: {len(h4)}")

        print("\n[1] DAILY SETUP")

        daily_setup = detect_daily_setup(daily)

        print(f"Daily setup: {daily_setup}")

        if not daily_setup:
            print("No daily setup detected")
            return

        direction = daily_setup.get("direction")
        setup_type = daily_setup.get("setup")

        if not direction:
            print("Daily setup has no direction")
            return

        print(f"Direction: {direction}")
        print(f"Setup: {setup_type}")

        print("\n[2] IMMEDIATE ENTRY CHECK")

        immediate_entry = daily_setup.get("entry")

        if immediate_entry is not None:
            print(f"Immediate entry detected: {immediate_entry}")

            build_and_display_signal(
                symbol=symbol,
                direction=direction,
                setup=setup_type,
                candle_data=daily.iloc[-1],
                market_data=daily,
                entry=float(immediate_entry),
                entry_type="ENGULFING",
            )

            return

        print("No immediate entry")

        print("\n[3] STRUCTURAL ENTRY CHECK")

        structural_entry = daily_setup.get("structural_entry")

        if structural_entry is None:
            print("No structural entry found")
            return

        entry_type = structural_entry.get("entry_type")
        entry_level = structural_entry.get("entry")

        print(f"Entry type: {entry_type}")
        print(f"Entry level: {entry_level}")

        if entry_level is None:
            print("Structural entry has no price")
            return

        print("\n[4] TREND BOS CHECK")

        h4_bos = detect_h4_bos(
            h4,
            direction=direction,
        )

        print(f"Trend BOS: {h4_bos}")

        if not h4_bos:
            print("No trend BOS confirmation")
            return

        print("\n[5] ENTRY SELECTION")

        selected_entry = select_best_entry(
            daily_data=daily,
            h4_data=h4,
            direction=direction,
            setup=setup_type,
        )

        print(f"Selected entry: {selected_entry}")

        if not selected_entry:
            print("No valid selected entry")
            return

        selected_price = selected_entry.get("entry")
        selected_type = selected_entry.get(
            "entry_type",
            entry_type,
        )

        if selected_price is None:
            print("Selected entry has no price")
            return

        print("\n[6] SIGNAL BUILDER")

        build_and_display_signal(
            symbol=symbol,
            direction=direction,
            setup=setup_type,
            candle_data=h4.iloc[-1],
            market_data=h4,
            entry=float(selected_price),
            entry_type=str(selected_type),
        )

    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}")


def main():
    print("FULL SIGNAL PIPELINE TEST")

    for symbol in SYMBOLS:
        test_symbol(symbol)


if __name__ == "__main__":
    main()
