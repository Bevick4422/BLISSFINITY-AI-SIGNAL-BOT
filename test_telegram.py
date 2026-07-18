import asyncio

from telegram.sender import send_signal

signal = {
    "pair": "BTC/USDT",
    "side": "BUY",
    "entry": 100000,
    "stop_loss": 99000,
    "tp1": 101500,
    "tp2": 103000,
    "take_profit": [101500, 103000],
    "rr": 3,
    "confidence": 92,
    "grade": "S",
    "score": 92,
    "reasons": [
        "Weekly Bias",
        "Daily BOS",
        "Liquidity"
    ]
}

asyncio.run(send_signal(signal))