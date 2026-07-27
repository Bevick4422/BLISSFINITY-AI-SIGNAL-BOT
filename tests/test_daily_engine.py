from scanner.market_scanner import fetch_market_data
from analysis.daily_setup.daily_engine import detect_daily_setup

symbol = "BTC/USDT:USDT"

market = fetch_market_data(symbol)

daily = market["1d"]

result = detect_daily_setup(daily)

print(result)