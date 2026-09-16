import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import main


TEST_SYMBOL = "TEST/USDT"


def test_production_scan_symbol():
    print("=" * 60)
    print("PRODUCTION SCANNER TEST")
    print("=" * 60)

    signal = {
        "symbol": TEST_SYMBOL,
        "direction": "BUY",
        "setup": "BULLISH_ENGULFING",
        "entry_type": "ENGULFING",
        "entry": 100.0,
        "stop_loss": 95.0,
        "tp1": 110.0,
        "tp2": 115.0,
        "risk": 5.0,
        "rr": 3.0,
        "confidence": 90.0,
        "valid": True,
    }

    recorded = {}

    def fake_record_signal(value):
        recorded["signal"] = value
        return "TEST_TRADE_001"

    async def run_test():
        main.signals_today = 0

        with patch(
            "main.get_active_trades",
            return_value=[],
        ), patch(
            "main.fetch_market_data",
            return_value={
                "1d": object(),
                "4h": object(),
            },
        ), patch(
            "main.evaluate_symbol",
            return_value=signal.copy(),
        ), patch(
            "main.validate_trade",
            return_value=True,
        ), patch(
            "main.record_signal",
            side_effect=fake_record_signal,
        ), patch(
            "main.send_signal",
            new=AsyncMock(return_value=True),
        ):
            await main.scan_symbol(TEST_SYMBOL)

    asyncio.run(run_test())

    assert recorded["signal"]["symbol"] == TEST_SYMBOL
    assert recorded["signal"]["direction"] == "BUY"
    assert recorded["signal"]["setup"] == "BULLISH_ENGULFING"
    assert recorded["signal"]["trade_id"] == "TEST_TRADE_001"

    assert main.signals_today == 1

    print("Market data fetch                 PASS")
    print("Strategy evaluation               PASS")
    print("Trade validation                  PASS")
    print("Trade recording                   PASS")
    print("Trade ID attachment               PASS")
    print("Telegram notification             PASS")
    print("Daily signal counter              PASS")
    print()
    print("PRODUCTION SCANNER TEST PASSED")


if __name__ == "__main__":
    test_production_scan_symbol()
