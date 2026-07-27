from analysis.setup_manager.setup_manager import (
    add_setup,
    load_setups,
    get_setup,
)

setup = {
    "symbol": "BTC/USDT:USDT",
    "direction": "BUY",
    "setup": "Bullish Engulfing",
    "level": 63738.3,
    "status": "WAITING_FOR_REJECTION",
}

add_setup(setup)

print(load_setups())

print(get_setup("BTC/USDT:USDT"))