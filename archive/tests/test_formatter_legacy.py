from signals.risk_manager import build_trade
from telegram.message_formatter import build_message

trade = build_trade("BUY", 109230)

print(build_message("BTC_USDT", "BUY", trade))

print("\nSUCCESS")
