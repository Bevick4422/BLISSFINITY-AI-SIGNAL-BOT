from engine.risk_engine import build_trade


def test_buy_trade():
    trade = build_trade(
        entry=100.0,
        stop_loss=90.0,
        direction="BUY",
    )

    assert trade["valid"] is True
    assert trade["entry"] == 100.0
    assert trade["stop_loss"] == 90.0
    assert trade["risk"] == 10.0
    assert trade["tp1"] == 120.0
    assert trade["tp2"] == 130.0
    assert trade["tp1_rr"] == 2.0
    assert trade["tp2_rr"] == 3.0
    assert trade["rr"] == 3.0


def test_sell_trade():
    trade = build_trade(
        entry=100.0,
        stop_loss=110.0,
        direction="SELL",
    )

    assert trade["valid"] is True
    assert trade["entry"] == 100.0
    assert trade["stop_loss"] == 110.0
    assert trade["risk"] == 10.0
    assert trade["tp1"] == 80.0
    assert trade["tp2"] == 70.0


def test_invalid_buy_stop():
    trade = build_trade(
        entry=100.0,
        stop_loss=105.0,
        direction="BUY",
    )

    assert trade["valid"] is False


if __name__ == "__main__":
    test_buy_trade()
    test_sell_trade()
    test_invalid_buy_stop()
    print("RISK TEST: PASS")
