from tracking.trade_manager import add_trade


async def execute(signal, telegram):

    if add_trade(signal):

        await telegram(signal)

        return True

    return False