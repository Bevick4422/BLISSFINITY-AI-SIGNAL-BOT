import os
from dotenv import load_dotenv

load_dotenv()

# ==================================================
# TELEGRAM
# ==================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==================================================
# EXCHANGE
# ==================================================

EXCHANGE = "mexc"

# ==================================================
# DEFAULT TIMEFRAMES
# ==================================================

TREND_TIMEFRAME = "4h"
ENTRY_TIMEFRAME = "15m"

# ==================================================
# RISK
# ==================================================

MAX_SIGNALS_PER_DAY = 3

MIN_CONFLUENCE_SCORE = 90

MIN_RISK_REWARD = 2.0

# ==================================================
# PAIRS
# ==================================================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT"
]
