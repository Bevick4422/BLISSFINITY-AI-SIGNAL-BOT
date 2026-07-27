from scanner.market_scanner import fetch_market_data
from engine.daily_bias import get_daily_bias

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)

bias = get_daily_bias(market["1d"])

print("Daily Bias:", bias)