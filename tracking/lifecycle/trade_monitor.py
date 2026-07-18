
"""
BLISSFINITY AI SIGNAL BOT
TRADE LIFECYCLE MONITOR
"""

from scanner.market_scanner import fetch_market_data

from tracking.trade_manager import (
    get_active_trades,
    update_trade,
)

from telegram.sender import (
    send_entry_message,
    send_tp_message,
    send_stop_message,
)


async def monitor_trades():

    trades = get_active_trades()

    for trade in trades:

        try:

            market = fetch_market_data(trade["pair"])

            df = market["15m"]

            price = float(df["close"].iloc[-1])

            # ===============================
            # BUY TRADE
            # ===============================

            if trade["side"] == "BUY":

                if not trade["entry_hit"] and price <= trade["entry"]:

                    update_trade(
                        trade["id"],
                        entry_hit=True
                    )

                    await send_entry_message(
                        trade["pair"],
                        trade["side"]
                    )

                elif (
                    trade["entry_hit"]
                    and not trade["tp1_hit"]
                    and price >= trade["take_profit"]
                ):

                    update_trade(
                        trade["id"],
                        tp1_hit=True,
                        breakeven=True
                    )

                    await send_tp_message(
                        trade["pair"],
                        trade["side"],
                        1,
                        trade["rr"]
                    )

                elif (
                    trade["tp1_hit"]
                    and not trade["tp2_hit"]
                    and price >= trade["take_profit"] * 1.01
                ):

                    update_trade(
                        trade["id"],
                        tp2_hit=True,
                        status="CLOSED"
                    )

                    await send_tp_message(
                        trade["pair"],
                        trade["side"],
                        2,
                        trade["rr"]
                    )

                elif (
                    trade["entry_hit"]
                    and not trade["sl_hit"]
                    and price <= trade["stop_loss"]
                ):

                    update_trade(
                        trade["id"],
                        sl_hit=True,
                        status="CLOSED"
                    )

                    await send_stop_message(
                        trade["pair"],
                        trade["side"]
                    )

            # ===============================
            # SELL TRADE
            # ===============================

            else:

                if not trade["entry_hit"] and price >= trade["entry"]:

                    update_trade(
                        trade["id"],
                        entry_hit=True
                    )

                    await send_entry_message(
                        trade["pair"],
                        trade["side"]
                    )

                elif (
                    trade["entry_hit"]
                    and not trade["tp1_hit"]
                    and price <= trade["take_profit"]
                ):

                    update_trade(
                        trade["id"],
                        tp1_hit=True,
                        breakeven=True
                    )

                    await send_tp_message(
                        trade["pair"],
                        trade["side"],
                        1,
                        trade["rr"]
                    )

                elif (
                    trade["tp1_hit"]
                    and not trade["tp2_hit"]
                    and price <= trade["take_profit"] * 0.99
                ):

                    update_trade(
                        trade["id"],
                        tp2_hit=True,
                        status="CLOSED"
                    )

                    await send_tp_message(
                        trade["pair"],
                        trade["side"],
                        2,
                        trade["rr"]
                    )

                elif (
                    trade["entry_hit"]
                    and not trade["sl_hit"]
                    and price >= trade["stop_loss"]
                ):

                    update_trade(
                        trade["id"],
                        sl_hit=True,
                        status="CLOSED"
                    )

                    await send_stop_message(
                        trade["pair"],
                        trade["side"]
                    )

        except Exception as e:

            print(f"Trade Monitor Error ({trade['pair']}): {e}")