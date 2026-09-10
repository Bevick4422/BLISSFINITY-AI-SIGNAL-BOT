from signal_engine.signal_builder import (
    build_signal,
    validate_signal,
    format_signal,
)


def display_signal(signal):
    print()

    if signal is None:
        print("Signal: None")
        return

    print("=" * 70)
    print("BUILT SIGNAL")
    print("=" * 70)

    print(f"Symbol      : {signal.get('symbol')}")
    print(f"Direction   : {signal.get('direction')}")
    print(f"Setup       : {signal.get('setup')}")
    print(f"Entry Type  : {signal.get('entry_type')}")
    print(f"Entry       : {signal.get('entry')}")
    print(f"Stop Loss   : {signal.get('stop_loss')}")
    print(f"Risk        : {signal.get('risk')}")
    print(f"TP1         : {signal.get('tp1')}")
    print(f"TP2         : {signal.get('tp2')}")
    print(f"Confidence  : {signal.get('confidence')}")
    print(f"RR          : {signal.get('rr')}")


def test_buy_signal():
    print()
    print("=" * 70)
    print("BUY SIGNAL TEST")
    print("=" * 70)

    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry=101.0,
        stop_loss=95.0,
        tp1=113.0,
        tp2=119.0,
        confidence=95.0,
        entry_type="LEFT_SHOULDER",
    )

    display_signal(signal)

    if signal is None:
        print("\nRESULT: BUY SIGNAL FAILED")
        return False

    if not validate_signal(signal):
        print("\nRESULT: BUY SIGNAL INVALID")
        return False

    if signal["stop_loss"] >= signal["entry"]:
        print("\nRESULT: BUY STOP INVALID")
        return False

    if signal["tp1"] <= signal["entry"]:
        print("\nRESULT: BUY TP1 INVALID")
        return False

    if signal["tp2"] <= signal["tp1"]:
        print("\nRESULT: BUY TP2 INVALID")
        return False

    print("\nRESULT: BUY SIGNAL SUCCESS")
    return True


def test_sell_signal():
    print()
    print("=" * 70)
    print("SELL SIGNAL TEST")
    print("=" * 70)

    signal = build_signal(
        symbol="ETH/USDT:USDT",
        direction="SELL",
        setup="A Shape",
        entry=99.0,
        stop_loss=105.0,
        tp1=87.0,
        tp2=81.0,
        confidence=92.0,
        entry_type="BREAK_RETEST",
    )

    display_signal(signal)

    if signal is None:
        print("\nRESULT: SELL SIGNAL FAILED")
        return False

    if not validate_signal(signal):
        print("\nRESULT: SELL SIGNAL INVALID")
        return False

    if signal["stop_loss"] <= signal["entry"]:
        print("\nRESULT: SELL STOP INVALID")
        return False

    if signal["tp1"] >= signal["entry"]:
        print("\nRESULT: SELL TP1 INVALID")
        return False

    if signal["tp2"] >= signal["tp1"]:
        print("\nRESULT: SELL TP2 INVALID")
        return False

    print("\nRESULT: SELL SIGNAL SUCCESS")
    return True


def test_invalid_direction():
    print()
    print("=" * 70)
    print("INVALID DIRECTION TEST")
    print("=" * 70)

    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction="INVALID",
        setup="V Shape",
        entry=101.0,
        stop_loss=95.0,
        tp1=113.0,
        tp2=119.0,
        confidence=90.0,
        entry_type="LEFT_SHOULDER",
    )

    display_signal(signal)

    if signal is None:
        print("\nRESULT: INVALID DIRECTION CORRECTLY REJECTED")
        return True

    print("\nRESULT: INVALID DIRECTION WAS NOT REJECTED")
    return False


def test_invalid_stop():
    print()
    print("=" * 70)
    print("INVALID STOP-LOSS TEST")
    print("=" * 70)

    signal = build_signal(
        symbol="BTC/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry=101.0,
        stop_loss=105.0,
        tp1=113.0,
        tp2=119.0,
        confidence=90.0,
        entry_type="FRESH_LEVEL",
    )

    display_signal(signal)

    if signal is None:
        print("\nRESULT: INVALID STOP CORRECTLY REJECTED")
        return True

    print("\nRESULT: INVALID STOP WAS NOT REJECTED")
    return False


def test_format():
    print()
    print("=" * 70)
    print("SIGNAL FORMAT TEST")
    print("=" * 70)

    signal = build_signal(
        symbol="SOL/USDT:USDT",
        direction="BUY",
        setup="V Shape",
        entry=101.0,
        stop_loss=95.0,
        tp1=113.0,
        tp2=119.0,
        confidence=88.0,
        entry_type="FRESH_LEVEL",
    )

    if signal is None:
        print("\nRESULT: FORMAT TEST FAILED")
        return False

    formatted = format_signal(signal)

    print()
    print(formatted)

    if formatted == "INVALID SIGNAL":
        print("\nRESULT: FORMAT TEST FAILED")
        return False

    required_text = (
        "BLISSFINITY SIGNAL",
        "SOL/USDT:USDT",
        "BUY",
        "V Shape",
        "Entry",
        "Stop Loss",
        "TP1",
        "TP2",
    )

    for text in required_text:
        if text not in formatted:
            print(
                f"\nRESULT: FORMAT TEST FAILED"
                f" | Missing: {text}"
            )
            return False

    if "TP3" in formatted:
        print("\nRESULT: FORMAT TEST FAILED | TP3 still present")
        return False

    print("\nRESULT: FORMAT TEST SUCCESS")
    return True


def main():
    print()
    print("=" * 70)
    print("BLISSFINITY SIGNAL | PRODUCTION SIGNAL BUILDER TEST")
    print("=" * 70)

    results = []

    results.append(("BUY SIGNAL", test_buy_signal()))
    results.append(("SELL SIGNAL", test_sell_signal()))
    results.append(("INVALID DIRECTION", test_invalid_direction()))
    results.append(("INVALID STOP", test_invalid_stop()))
    results.append(("FORMAT", test_format()))

    print()
    print("=" * 70)
    print("FINAL TEST RESULTS")
    print("=" * 70)

    passed = 0

    for name, result in results:
        status = "PASSED" if result else "FAILED"

        print(f"{name:<25} {status}")

        if result:
            passed += 1

    print()
    print(f"Passed: {passed}/{len(results)}")

    if passed == len(results):
        print("SIGNAL BUILDER TEST SUCCESS")
        return True

    print("SIGNAL BUILDER TEST FAILED")
    return False


if __name__ == "__main__":
    main()