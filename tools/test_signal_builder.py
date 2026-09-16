from signal_engine.signal_builder import (
    build_signal,
    validate_signal,
)


def test_buy_signal():
    signal = build_signal(
        symbol="TEST/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry_type="BREAK_RETEST",
        entry=100.0,
        stop_loss=95.0,
        tp1=110.0,
        tp2=115.0,
        confidence=90.0,
    )

    assert isinstance(signal, dict)
    assert signal["direction"] == "BUY"
    assert signal["entry"] == 100.0
    assert signal["stop_loss"] == 95.0
    assert signal["tp1"] == 110.0
    assert signal["tp2"] == 115.0
    assert validate_signal(signal) is True


def test_sell_signal():
    signal = build_signal(
        symbol="TEST/USDT:USDT",
        direction="SELL",
        setup="A Shape",
        entry_type="BREAK_RETEST",
        entry=100.0,
        stop_loss=105.0,
        tp1=90.0,
        tp2=85.0,
        confidence=90.0,
    )

    assert isinstance(signal, dict)
    assert signal["direction"] == "SELL"
    assert signal["entry"] == 100.0
    assert signal["stop_loss"] == 105.0
    assert signal["tp1"] == 90.0
    assert signal["tp2"] == 85.0
    assert validate_signal(signal) is True


def test_invalid_direction():
    signal = build_signal(
        symbol="TEST/USDT:USDT",
        direction="INVALID",
        setup="V Shape",
        entry_type="BREAK_RETEST",
        entry=100.0,
        stop_loss=95.0,
        tp1=110.0,
        tp2=115.0,
        confidence=90.0,
    )

    assert signal is None or validate_signal(signal) is False


def test_invalid_stop():
    signal = build_signal(
        symbol="TEST/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry_type="BREAK_RETEST",
        entry=100.0,
        stop_loss=105.0,
        tp1=110.0,
        tp2=115.0,
        confidence=90.0,
    )

    assert signal is None or validate_signal(signal) is False


def test_format():
    signal = build_signal(
        symbol="TEST/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry_type="BREAK_RETEST",
        entry=100.0,
        stop_loss=95.0,
        tp1=110.0,
        tp2=115.0,
        confidence=90.0,
    )

    assert isinstance(signal, dict)
    assert "symbol" in signal
    assert "direction" in signal
    assert "setup" in signal
    assert "entry" in signal
    assert "stop_loss" in signal
    assert "tp1" in signal
    assert "tp2" in signal
