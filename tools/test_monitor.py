from tracking.monitor import monitor_trade


def make_trade(direction):
    return {
        "id": "TEST_MONITOR_001",
        "trade_id": "TEST_MONITOR_001",
        "direction": direction,
        "entry": 100.0,
        "stop_loss": 90.0 if direction == "BUY" else 110.0,
        "tp1": 120.0 if direction == "BUY" else 80.0,
        "tp2": 130.0 if direction == "BUY" else 70.0,
        "state": "OPEN",
        "status": "OPEN",
        "tp1_hit": False,
        "tp2_hit": False,
        "stop_loss_hit": False,
        "result": None,
        "result_percent": None,
        "r_multiple": None,
        "closed_at": None,
    }


def test_buy_tp1():
    trade = make_trade("BUY")
    result = monitor_trade(trade, 120)
    assert result["tp1_hit"] is True
    assert result["state"] == "BREAK_EVEN"
    print("BUY TP1: PASSED")


def test_buy_tp2():
    trade = make_trade("BUY")
    result = monitor_trade(trade, 120)
    result = monitor_trade(result, 130)
    assert result["tp2_hit"] is True
    assert result["result"] == "WIN"
    assert result["status"] == "CLOSED"
    assert result["r_multiple"] == 3.0
    print("BUY TP2: PASSED")


def test_buy_stop():
    trade = make_trade("BUY")
    result = monitor_trade(trade, 90)
    assert result["result"] == "LOSS"
    assert result["status"] == "CLOSED"
    assert result["r_multiple"] == -1.0
    print("BUY STOP: PASSED")


def test_sell_tp2():
    trade = make_trade("SELL")
    result = monitor_trade(trade, 80)
    result = monitor_trade(result, 70)
    assert result["tp2_hit"] is True
    assert result["result"] == "WIN"
    assert result["r_multiple"] == 3.0
    print("SELL TP2: PASSED")


def test_sell_stop():
    trade = make_trade("SELL")
    result = monitor_trade(trade, 110)
    assert result["result"] == "LOSS"
    assert result["status"] == "CLOSED"
    assert result["r_multiple"] == -1.0
    print("SELL STOP: PASSED")


if __name__ == "__main__":
    test_buy_tp1()
    test_buy_tp2()
    test_buy_stop()
    test_sell_tp2()
    test_sell_stop()

    print("MONITOR TEST SUCCESS")