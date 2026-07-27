from scanner.market_scanner import fetch_market_data
from analysis.bos.bos_engine import (
    bullish_bos,
    bearish_bos,
)

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)

h4 = market["4h"]

print("Bullish BOS:", bullish_bos(h4))
print("Bearish BOS:", bearish_bos(h4))