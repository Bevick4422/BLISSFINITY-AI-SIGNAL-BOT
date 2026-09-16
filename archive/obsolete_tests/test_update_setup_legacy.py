from analysis.setup_manager.setup_manager import (
    update_setup,
    get_setup,
)

update_setup(
    "BTC/USDT:USDT",
    rejection=True,
    status="WAITING_FOR_BOS",
)

print(get_setup("BTC/USDT:USDT"))