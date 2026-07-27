from scanner.market_scanner import fetch_market_data

from analysis.setup_manager.setup_manager import (
    get_setup,
    update_setup,
)

from analysis.bos.bos_engine import (
    bullish_bos,
    bearish_bos,
)

symbol = "BTC/USDT:USDT"

setup = get_setup(symbol)

if setup is None:
    print("No active setup.")
    raise SystemExit

market = fetch_market_data(symbol)
h4 = market["4h"]

if setup["direction"] == "BUY":

    if bullish_bos(h4):

        update_setup(
            symbol,
            bos=True,
            status="READY_TO_SIGNAL",
        )

        print("BUY setup confirmed by BOS.")

    else:

        print("Waiting for Bullish BOS.")

elif setup["direction"] == "SELL":

    if bearish_bos(h4):

        update_setup(
            symbol,
            bos=True,
            status="READY_TO_SIGNAL",
        )

        print("SELL setup confirmed by BOS.")

    else:

        print("Waiting for Bearish BOS.")