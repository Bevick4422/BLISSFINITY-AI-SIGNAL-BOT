
from market_data.fetcher import fetch_market_data
from analysis.daily_setup.daily_engine import detect_daily_setup
from analysis.h4_bos.h4_bos_engine import detect_h4_bos
from engine.strategy_engine import evaluate_symbol


SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]


def inspect_symbol(symbol):
    print("\n" + "=" * 70)
    print(f"SYMBOL: {symbol}")
    print("=" * 70)

    try:
        market = fetch_market_data(symbol)

        daily = market.get("1d")
        h4 = market.get("4h")

        if daily is None or h4 is None:
            print("MARKET DATA: MISSING")
            return

        print(f"Daily candles: {len(daily)}")
        print(f"H4 candles: {len(h4)}")

        daily_setup = detect_daily_setup(daily)
        print("\nDAILY SETUP")
        print(daily_setup)

        daily_direction = None
        if isinstance(daily_setup, dict):
            daily_direction = daily_setup.get("direction")

        print("\nH4 BOS")
        h4_bos = detect_h4_bos(h4)
        print(h4_bos)

        print("\nFINAL STRATEGY RESULT")
        result = evaluate_symbol(symbol, market)
        print(result)

        if isinstance(result, dict):
            print("\nFINAL DIRECTION:", result.get("direction"))
            print("FINAL STATUS:", result.get("status"))

        print("\nDIRECTION COMPARISON")
        print("Daily direction:", daily_direction)
        print("H4 BOS direction:", h4_bos.get("direction") if isinstance(h4_bos, dict) else None)

    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")


def main():
    for symbol in SYMBOLS:
        inspect_symbol(symbol)


if __name__ == "__main__":
    main()
