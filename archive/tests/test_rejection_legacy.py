from scanner.market_scanner import fetch_market_data
from analysis.daily_setup.keylevels import (
    find_v_shape,
    find_a_shape,
)
from analysis.rejection.rejection_engine import (
    bullish_rejection,
    bearish_rejection,
)

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)
daily = market["1d"]

last_candle = daily.iloc[-1]

support = find_v_shape(daily)
resistance = find_a_shape(daily)

print("Support:", support)
print("Resistance:", resistance)

print("Bullish Rejection:", bullish_rejection(last_candle, support))
print("Bearish Rejection:", bearish_rejection(last_candle, resistance))