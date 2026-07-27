from scanner.market_scanner import fetch_market_data
from engine.risk_engine import build_trade

market = fetch_market_data("BTC/USDT:USDT")

trade = build_trade(
    "BUY",
    market["4h"].iloc[-1]
)

print(trade)