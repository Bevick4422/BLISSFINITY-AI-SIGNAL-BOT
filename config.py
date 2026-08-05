
"""
BLISSFINITY AI SIGNAL BOT
CONFIGURATION
"""

import requests

# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_TOKEN = "8908134517:AAHVTOQdR0f01XDlZfOIvd9yiYNev_t7K-I"

TELEGRAM_CHAT_ID = "-1004459723300"

# ==========================================
# BOT SETTINGS
# ==========================================

SCAN_INTERVAL = 60

MAX_SIGNALS_PER_SCAN = 4

MAX_PAIRS = 100

# ==========================================
# MEXC FUTURES SYMBOL LOADER
# ==========================================


def get_symbols():

    try:

        url = "https://contract.mexc.com/api/v1/contract/detail"

        response = requests.get(url, timeout=10)

        data = response.json()

        if data["success"] is False:
            return []

        contracts = data["data"]

        symbols = []

        for contract in contracts:

            if contract["state"] != 0:
                continue

            symbol = contract["symbol"]

            if "_USDT" not in symbol:
                continue

            pair = symbol.replace("_", "/")

            symbols.append(pair)

        symbols.sort()

        return symbols[:MAX_PAIRS]

    except Exception as e:

        print("Unable to load futures markets:", e)

        return []


SYMBOLS = get_symbols()