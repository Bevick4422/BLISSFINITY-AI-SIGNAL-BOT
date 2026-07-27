from scanner.market_scanner import fetch_market_data
from analysis.daily_setup.keylevels import find_v_shape, find_a_shape

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)

daily = market["1d"]

v_level = find_v_shape(daily)
a_level = find_a_shape(daily)

print("V Shape Support :", v_level)
print("A Shape Resistance :", a_level)