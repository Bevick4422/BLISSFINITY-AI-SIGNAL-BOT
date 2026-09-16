from pathlib import Path
import sys
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import SYMBOLS
from market_data.fetcher import fetch_market_data
from analysis.candle_gate import get_completed_candles
from analysis.daily_structure.daily_structure_engine import detect_daily_setup


def main():
    print("=" * 100)
    print("LIVE DAILY ENGULFING / A-V AUDIT")
    print("=" * 100)

    engulfing_count = 0
    no_engulfing_count = 0
    errors = 0

    for i, symbol in enumerate(SYMBOLS, 1):
        print(f"\n[{i}/{len(SYMBOLS)}] {symbol}")

        try:
            market_data = fetch_market_data(symbol)

            daily = market_data.get("1d")

            if daily is None or daily.empty:
                print("  DAILY DATA       : MISSING")
                continue

            # IMPORTANT:
            # get_completed_candles requires the timeframe.
            daily = get_completed_candles(daily, "1d")

            if daily is None or len(daily) < 8:
                print("  DAILY DATA       : INSUFFICIENT")
                continue

            result = detect_daily_setup(daily)

            setup = result.get("setup")
            direction = result.get("direction")
            trend = result.get("trend")
            level = result.get("level")
            level_index = result.get("level_index")
            reason = result.get("reason")

            if setup in ("Bullish Engulfing", "Bearish Engulfing"):
                engulfing_count += 1

                print("  TYPE             : ENGULFING")
                print(f"  TREND            : {trend}")
                print(f"  SETUP            : {setup}")
                print(f"  DIRECTION        : {direction}")
                print(f"  LEVEL            : {level}")
                print(f"  LEVEL INDEX      : {level_index}")
                print(f"  REASON            : {reason}")

                print("  RAW DAILY RESULT:")
                pprint(result, sort_dicts=False)

            else:
                no_engulfing_count += 1

        except Exception as exc:
            errors += 1
            print(
                f"  ERROR            : "
                f"{type(exc).__name__}: {exc}"
            )

    print("\n" + "=" * 100)
    print("AUDIT SUMMARY")
    print("=" * 100)
    print(f"TOTAL SYMBOLS      : {len(SYMBOLS)}")
    print(f"ENGULFINGS FOUND   : {engulfing_count}")
    print(f"NO ENGULFING       : {no_engulfing_count}")
    print(f"ERRORS             : {errors}")
    print("=" * 100)


if __name__ == "__main__":
    main()
