"""
=========================================================
BLISSFINITY SIGNAL
Trade Tracker Duplicate Protection Test
=========================================================

Tests:

1. First signal is recorded.
2. Same signal is rejected as duplicate.
3. Same signal repeated again remains one trade.
4. Different signal is accepted.
5. TP1 fires once.
6. Repeated TP1 checks do not fire again.
7. TP2 closes the trade once.
8. Repeated TP2 checks are ignored.
9. Closed trades cannot be updated.
10. SL fires once on a separate trade.
11. Repeated SL checks are ignored.
12. Trade data persists.
13. Performance calculation works.
=========================================================
"""

from __future__ import annotations

from tracking.trade_tracker import (
    TRADE_FILE,
    record_signal,
    update_trade,
    get_trade,
    get_performance,
)


# ==========================================================
# CLEAN TEST STORAGE
# ==========================================================

def reset_storage():

    if TRADE_FILE.exists():

        TRADE_FILE.unlink()

        print(
            "TEST STORAGE RESET"
        )


# ==========================================================
# DISPLAY TRADE
# ==========================================================

def show_trade(trade):

    print()
    print(
        "TRADE"
    )
    print(
        "-" * 60
    )

    if trade is None:

        print(
            "Trade : None"
        )

        return

    print(
        f"Trade ID      : {trade.get('trade_id')}"
    )

    print(
        f"Symbol        : {trade.get('symbol')}"
    )

    print(
        f"Direction     : {trade.get('direction')}"
    )

    print(
        f"Entry         : {trade.get('entry')}"
    )

    print(
        f"Stop Loss     : {trade.get('stop_loss')}"
    )

    print(
        f"TP1           : {trade.get('tp1')}"
    )

    print(
        f"TP2           : {trade.get('tp2')}"
    )

    print(
        f"Status        : {trade.get('status')}"
    )

    print(
        f"TP1 Hit       : {trade.get('tp1_hit')}"
    )

    print(
        f"TP2 Hit       : {trade.get('tp2_hit')}"
    )

    print(
        f"SL Hit        : {trade.get('stop_loss_hit')}"
    )

    print(
        f"Last Event    : {trade.get('last_event')}"
    )

    print(
        f"Result        : {trade.get('result')}"
    )

    print(
        f"Result %      : {trade.get('result_percent')}"
    )

    print(
        f"R Multiple    : {trade.get('r_multiple')}"
    )


# ==========================================================
# MAIN TEST
# ==========================================================

def main():

    reset_storage()

    print()
    print(
        "=" * 70
    )

    print(
        "BLISSFINITY SIGNAL | "
        "DUPLICATE + TP/SL PROTECTION TEST"
    )

    print(
        "=" * 70
    )

    passed = 0
    total = 0

    # ======================================================
    # 1. FIRST SIGNAL
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[1] FIRST SIGNAL"
    )

    print(
        "=" * 70
    )

    trade1 = record_signal(

        symbol="TEST/BTC",

        direction="BUY",

        setup="V Shape",

        entry=100.0,

        stop_loss=95.0,

        tp1=105.0,

        tp2=110.0,

        confidence=95.0,

        signal_id="DUPLICATE_TEST_001",
    )

    show_trade(
        trade1
    )

    total += 1

    if trade1 is not None:

        print(
            "\nRESULT: FIRST SIGNAL RECORDED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: FIRST SIGNAL FAILED"
        )

    # ======================================================
    # 2. DUPLICATE SIGNAL
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[2] DUPLICATE SIGNAL"
    )

    print(
        "=" * 70
    )

    duplicate1 = record_signal(

        symbol="TEST/BTC",

        direction="BUY",

        setup="V Shape",

        entry=100.0,

        stop_loss=95.0,

        tp1=105.0,

        tp2=110.0,

        confidence=95.0,
    )

    show_trade(
        duplicate1
    )

    total += 1

    if (
        duplicate1 is not None
        and trade1 is not None
        and duplicate1["trade_id"]
        == trade1["trade_id"]
    ):

        print(
            "\nRESULT: DUPLICATE CORRECTLY REJECTED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: DUPLICATE WAS CREATED"
        )

    # ======================================================
    # 3. DUPLICATE AGAIN
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[3] DUPLICATE SIGNAL AGAIN"
    )

    print(
        "=" * 70
    )

    duplicate2 = record_signal(

        symbol="TEST/BTC",

        direction="BUY",

        setup="V Shape",

        entry=100.0,

        stop_loss=95.0,

        tp1=105.0,

        tp2=110.0,

        confidence=95.0,
    )

    show_trade(
        duplicate2
    )

    total += 1

    if (
        duplicate2 is not None
        and trade1 is not None
        and duplicate2["trade_id"]
        == trade1["trade_id"]
    ):

        print(
            "\nRESULT: SECOND DUPLICATE CORRECTLY REJECTED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: SECOND DUPLICATE FAILED"
        )

    # ======================================================
    # 4. TP1
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[4] TP1"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade1["trade_id"],

        105.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["last_event"]
        == "TP1_HIT"
        and result["tp1_hit"] is True
        and result["status"] == "OPEN"
    ):

        print(
            "\nRESULT: TP1 HIT SUCCESSFULLY"
        )

        passed += 1

    else:

        print(
            "\nRESULT: TP1 FAILED"
        )

    # ======================================================
    # 5. TP1 REPEAT
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[5] TP1 REPEAT"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade1["trade_id"],

        106.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["tp1_hit"] is True
        and result["last_event"]
        == "NO_CHANGE"
    ):

        print(
            "\nRESULT: DUPLICATE TP1 CORRECTLY IGNORED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: DUPLICATE TP1 WAS NOT IGNORED"
        )

    # ======================================================
    # 6. TP1 REPEAT AGAIN
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[6] TP1 REPEAT AGAIN"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade1["trade_id"],

        107.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["tp1_hit"] is True
        and result["last_event"]
        == "NO_CHANGE"
    ):

        print(
            "\nRESULT: SECOND DUPLICATE TP1 IGNORED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: SECOND TP1 UPDATE FAILED"
        )

    # ======================================================
    # 7. TP2
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[7] TP2"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade1["trade_id"],

        110.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["last_event"]
        == "TP2_HIT"
        and result["tp2_hit"] is True
        and result["status"] == "CLOSED"
        and result["result"] == "WIN"
    ):

        print(
            "\nRESULT: TP2 CLOSED TRADE AS WIN"
        )

        passed += 1

    else:

        print(
            "\nRESULT: TP2 FAILED"
        )

    # ======================================================
    # 8. TP2 REPEAT
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[8] TP2 REPEAT"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade1["trade_id"],

        110.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["status"] == "CLOSED"
        and result["last_event"]
        == "TRADE_CLOSED"
    ):

        print(
            "\nRESULT: CLOSED TRADE CORRECTLY IGNORED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: CLOSED TRADE WAS UPDATED"
        )

    # ======================================================
    # 9. DIFFERENT SIGNAL
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[9] DIFFERENT SIGNAL"
    )

    print(
        "=" * 70
    )

    trade2 = record_signal(

        symbol="TEST/ETH",

        direction="SELL",

        setup="A Shape",

        entry=200.0,

        stop_loss=205.0,

        tp1=195.0,

        tp2=190.0,

        confidence=92.0,

        signal_id="DUPLICATE_TEST_002",
    )

    show_trade(
        trade2
    )

    total += 1

    if (
        trade2 is not None
        and trade1 is not None
        and trade2["trade_id"]
        != trade1["trade_id"]
    ):

        print(
            "\nRESULT: DIFFERENT SIGNAL ACCEPTED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: DIFFERENT SIGNAL REJECTED"
        )

    # ======================================================
    # 10. STOP LOSS
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[10] STOP LOSS"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade2["trade_id"],

        205.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["last_event"]
        == "STOP_LOSS_HIT"
        and result["stop_loss_hit"] is True
        and result["status"] == "CLOSED"
        and result["result"] == "LOSS"
    ):

        print(
            "\nRESULT: STOP LOSS CLOSED TRADE"
        )

        passed += 1

    else:

        print(
            "\nRESULT: STOP LOSS FAILED"
        )

    # ======================================================
    # 11. STOP LOSS REPEAT
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[11] STOP LOSS REPEAT"
    )

    print(
        "=" * 70
    )

    result = update_trade(

        trade2["trade_id"],

        205.0,
    )

    show_trade(
        result
    )

    total += 1

    if (
        result is not None
        and result["status"] == "CLOSED"
        and result["last_event"]
        == "TRADE_CLOSED"
    ):

        print(
            "\nRESULT: DUPLICATE SL CORRECTLY IGNORED"
        )

        passed += 1

    else:

        print(
            "\nRESULT: DUPLICATE SL FAILED"
        )

    # ======================================================
    # 12. PERSISTENCE
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[12] PERSISTENCE"
    )

    print(
        "=" * 70
    )

    saved_trade = get_trade(
        "DUPLICATE_TEST_001"
    )

    total += 1

    if (
        saved_trade is not None
        and saved_trade["status"]
        == "CLOSED"
        and saved_trade["result"]
        == "WIN"
    ):

        print(
            "RESULT: PERSISTENCE SUCCESS"
        )

        passed += 1

    else:

        print(
            "RESULT: PERSISTENCE FAILED"
        )

    # ======================================================
    # 13. PERFORMANCE
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "[13] PERFORMANCE"
    )

    print(
        "=" * 70
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

    # ======================================================
    # FINAL RESULT
    # ======================================================

    print()
    print(
        "=" * 70
    )

    print(
        "TEST SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        f"Passed : {passed}/{total}"
    )

    if passed == total:

        print()
        print(
            "RESULT: ALL DUPLICATE + TP/SL "
            "TESTS PASSED"
        )

    else:

        print()
        print(
            "RESULT: SOME TESTS FAILED"
        )

    print()
    print(
        "=" * 70
    )

    print(
        "DUPLICATE PROTECTION TEST COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()