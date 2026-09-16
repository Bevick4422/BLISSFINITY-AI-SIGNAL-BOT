"""
=========================================================
BLISSFINITY SIGNAL BOT
Production Trade Signal Integration Test
=========================================================

Tests:

Market Data
    ↓
ATR
    ↓
Structure Stop
    ↓
Risk Engine
    ↓
Production Signal Builder
    ↓
Signal Validation
"""

from __future__ import annotations

import pandas as pd

from engine.strategy_engine import build_production_trade_signal


# =========================================================
# MARKET DATA
# =========================================================

def create_market_data(
    start_price: float = 100.0,
    candles: int = 40,
) -> pd.DataFrame:

    rows = []

    price = float(start_price)

    for _ in range(candles):

        rows.append(
            {
                "open": price,
                "high": price + 2.0,
                "low": price - 2.0,
                "close": price + 1.0,
                "volume": 1000.0,
            }
        )

        price += 1.0

    return pd.DataFrame(rows)


# =========================================================
# DISPLAY
# =========================================================

def display_signal(signal):

    print()
    print("SIGNAL")
    print("-" * 60)

    if signal is None:

        print("Signal      : None")

        return

    fields = (
        "symbol",
        "direction",
        "setup",
        "entry_type",
        "entry",
        "stop_loss",
        "risk",
        "tp1",
        "tp2",
        "tp3",
        "rr",
        "confidence",
        "atr",
        "status",
        "valid",
        "production_signal",
        "risk_engine",
    )

    labels = {
        "symbol": "Symbol",
        "direction": "Direction",
        "setup": "Setup",
        "entry_type": "Entry Type",
        "entry": "Entry",
        "stop_loss": "Stop Loss",
        "risk": "Risk",
        "tp1": "TP1",
        "tp2": "TP2",
        "tp3": "TP3",
        "rr": "RR",
        "confidence": "Confidence",
        "atr": "ATR",
        "status": "Status",
        "valid": "Valid",
        "production_signal": "Production",
        "risk_engine": "Risk Engine",
    }

    for field in fields:

        print(
            f"{labels[field]:<14}: "
            f"{signal.get(field)}"
        )


# =========================================================
# TEST
# =========================================================

def test_production_buy():

    print()
    print("=" * 70)
    print("BLISSFINITY SIGNAL | PRODUCTION TRADE SIGNAL TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # MARKET DATA
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("[1] MARKET DATA")
    print("=" * 70)

    h4 = create_market_data()

    print(
        f"Candles      : {len(h4)}"
    )

    print(
        f"Latest Open  : {h4.iloc[-1]['open']}"
    )

    print(
        f"Latest High  : {h4.iloc[-1]['high']}"
    )

    print(
        f"Latest Low   : {h4.iloc[-1]['low']}"
    )

    print(
        f"Latest Close : {h4.iloc[-1]['close']}"
    )

    # -----------------------------------------------------
    # PRODUCTION SIGNAL
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("[2] BUILD PRODUCTION SIGNAL")
    print("=" * 70)

    entry = float(
        h4.iloc[-1]["close"]
    )

    signal = build_production_trade_signal(

        symbol="TEST/BTC",

        direction="BUY",

        setup="V Shape",

        entry_type="LEFT_SHOULDER",

        entry=entry,

        confidence=95,

        current_price=entry,

        h4=h4,
    )

    display_signal(
        signal
    )

    if signal is None:

        print()
        print(
            "RESULT: PRODUCTION SIGNAL FAILED"
        )

        return False

    print()
    print(
        "RESULT: PRODUCTION SIGNAL CREATED"
    )

    # -----------------------------------------------------
    # STRUCTURE VALIDATION
    # -----------------------------------------------------

    print()
    print("=" * 70)
    print("[3] VALIDATION")
    print("=" * 70)

    direction = signal.get(
        "direction"
    )

    entry_price = float(
        signal["entry"]
    )

    stop_loss = float(
        signal["stop_loss"]
    )

    tp1 = float(
        signal["tp1"]
    )

    tp2 = float(
        signal["tp2"]
    )

    tp3 = float(
        signal["tp3"]
    )

    valid = True

    if direction != "BUY":

        print(
            "FAIL: Direction is not BUY"
        )

        valid = False

    if stop_loss >= entry_price:

        print(
            "FAIL: BUY stop-loss is not below entry"
        )

        valid = False

    if tp1 <= entry_price:

        print(
            "FAIL: TP1 is not above entry"
        )

        valid = False

    if tp2 <= tp1:

        print(
            "FAIL: TP2 is not above TP1"
        )

        valid = False

    if tp3 <= tp2:

        print(
            "FAIL: TP3 is not above TP2"
        )

        valid = False

    if signal.get("valid") is not True:

        print(
            "FAIL: Signal valid flag is not True"
        )

        valid = False

    if signal.get("production_signal") is not True:

        print(
            "FAIL: Production flag missing"
        )

        valid = False

    if signal.get("risk_engine") is not True:

        print(
            "FAIL: Risk engine flag missing"
        )

        valid = False

    if valid:

        print(
            "RESULT: PRODUCTION SIGNAL VALID"
        )

    else:

        print(
            "RESULT: PRODUCTION SIGNAL INVALID"
        )

    return valid


# =========================================================
# MAIN
# =========================================================

def main():

    passed = test_production_buy()

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if passed:

        print(
            "ALL PRODUCTION TRADE SIGNAL TESTS PASSED"
        )

    else:

        print(
            "PRODUCTION TRADE SIGNAL TEST FAILED"
        )

    print()
    print("=" * 70)
    print(
        "PRODUCTION TRADE SIGNAL TEST COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":

    main()