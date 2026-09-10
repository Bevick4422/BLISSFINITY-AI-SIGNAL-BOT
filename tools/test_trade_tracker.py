"""
=========================================================
BLISSFINITY SIGNAL
Trade Tracker Test
=========================================================

Tests:

1. BUY trade
2. TP1 detection
3. TP2 detection
4. SELL trade
5. Stop Loss detection
6. Performance summary
=========================================================
"""

from tracking.trade_tracker import (
    record_signal,
    update_trade,
    get_performance,
)


def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:

    print_header(
        "BLISSFINITY SIGNAL | TRADE TRACKER TEST"
    )

    # =====================================================
    # BUY TEST
    # =====================================================

    print_header("BUY TRADE TEST")

    buy = record_signal(
        symbol="BTC/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry=100.0,
        stop_loss=95.0,
        tp1=105.0,
        tp2=110.0,
        confidence=90,
        signal_id="TEST_BUY_001",
    )

    if buy is None:
        print("BUY TEST FAILED")
        return

    print(
        f"Trade ID    : {buy['trade_id']}"
    )

    print(
        f"Entry       : {buy['entry']}"
    )

    print(
        f"Stop Loss   : {buy['stop_loss']}"
    )

    print(
        f"TP1         : {buy['tp1']}"
    )

    print(
        f"TP2         : {buy['tp2']}"
    )

    # =====================================================
    # BUY TP1
    # =====================================================

    print()
    print("[BUY] Testing TP1...")

    buy = update_trade(
        "TEST_BUY_001",
        105.0,
    )

    print(
        f"TP1 Hit     : {buy['tp1_hit']}"
    )

    print(
        f"Status      : {buy['status']}"
    )

    # =====================================================
    # BUY TP2
    # =====================================================

    print()
    print("[BUY] Testing TP2...")

    buy = update_trade(
        "TEST_BUY_001",
        110.0,
    )

    print(
        f"TP2 Hit     : {buy['tp2_hit']}"
    )

    print(
        f"Status      : {buy['status']}"
    )

    print(
        f"Result      : {buy['result']}"
    )

    print(
        f"Result %    : "
        f"{buy['result_percent']:.2f}%"
    )

    print(
        f"R Multiple  : "
        f"{buy['r_multiple']:.2f}R"
    )

    # =====================================================
    # SELL TEST
    # =====================================================

    print_header("SELL TRADE TEST")

    sell = record_signal(
        symbol="ETH/USDT:USDT",
        direction="SELL",
        setup="Bearish Engulfing",
        entry=100.0,
        stop_loss=105.0,
        tp1=95.0,
        tp2=90.0,
        confidence=92,
        signal_id="TEST_SELL_001",
    )

    if sell is None:
        print("SELL TEST FAILED")
        return

    print(
        f"Trade ID    : {sell['trade_id']}"
    )

    print(
        f"Entry       : {sell['entry']}"
    )

    print(
        f"Stop Loss   : {sell['stop_loss']}"
    )

    print(
        f"TP1         : {sell['tp1']}"
    )

    print(
        f"TP2         : {sell['tp2']}"
    )

    # =====================================================
    # SELL STOP LOSS
    # =====================================================

    print()
    print("[SELL] Testing Stop Loss...")

    sell = update_trade(
        "TEST_SELL_001",
        105.0,
    )

    print(
        f"SL Hit       : "
        f"{sell['stop_loss_hit']}"
    )

    print(
        f"Status       : "
        f"{sell['status']}"
    )

    print(
        f"Result       : "
        f"{sell['result']}"
    )

    print(
        f"Result %     : "
        f"{sell['result_percent']:.2f}%"
    )

    print(
        f"R Multiple   : "
        f"{sell['r_multiple']:.2f}R"
    )

    # =====================================================
    # PERFORMANCE
    # =====================================================

    print_header(
        "PERFORMANCE SUMMARY"
    )

    performance = get_performance()

    print(
        f"Total Trades : "
        f"{performance['total_trades']}"
    )

    print(
        f"Open Trades  : "
        f"{performance['open_trades']}"
    )

    print(
        f"Closed Trades: "
        f"{performance['closed_trades']}"
    )

    print(
        f"Wins         : "
        f"{performance['wins']}"
    )

    print(
        f"Losses       : "
        f"{performance['losses']}"
    )

    print(
        f"Win Rate     : "
        f"{performance['win_rate']:.2f}%"
    )

    print(
        f"Total %      : "
        f"{performance['total_percent']:.2f}%"
    )

    print(
        f"Total R      : "
        f"{performance['total_r']:.2f}R"
    )

    print_header(
        "TRADE TRACKER TEST COMPLETE"
    )


if __name__ == "__main__":
    main()