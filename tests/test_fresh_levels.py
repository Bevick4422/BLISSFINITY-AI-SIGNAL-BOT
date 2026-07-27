from scanner.market_scanner import fetch_market_data

from analysis.daily_setup.keylevels import (
    find_v_shape,
    find_a_shape
)

from analysis.daily_setup.fresh_levels import (
    is_fresh_support,
    is_fresh_resistance
)

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)

daily = market["1d"]

support = find_v_shape(daily)
resistance = find_a_shape(daily)

print("Support:", support)
print("Fresh Support:", is_fresh_support(daily, support))

print("Resistance:", resistance)
print("Fresh Resistance:", is_fresh_resistance(daily, resistance))