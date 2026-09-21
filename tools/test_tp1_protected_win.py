import tempfile
from pathlib import Path

import tracking.trade_tracker as tracker

# Isolate all test data from the live trade file.
tracker.TRADE_FILE = Path(tempfile.gettempdir()) / "blissfinity_tp1_protected_regression.json"
tracker.TRADE_FILE.unlink(missing_ok=True)

def create_trade(symbol, direction, entry, sl, tp1, tp2):
    trade_id = tracker.record_signal({
        "symbol": symbol,
        "direction": direction,
        "setup": "Regression Test",
        "entry": entry,
        "stop_loss": sl,
        "tp1": tp1,
        "tp2": tp2,
        "risk": abs(entry - sl),
        "rr": 2,
        "confidence": 90,
    })
    assert trade_id, f"Failed to record {symbol}"
    return trade_id

# BUY: entry -> TP1 -> return to entry.
buy_id = create_trade("TEST_BUY_PROTECTED", "BUY", 100, 95, 105, 110)

trade = tracker.update_trade(buy_id, 100, candle_high=100, candle_low=99)
assert trade["status"] == "OPEN", trade

trade = tracker.update_trade(buy_id, 105, candle_high=106, candle_low=101)
assert trade["tp1_hit"] is True, trade
assert trade["break_even"] is True, trade
assert trade["stop_loss"] == 100, trade

trade = tracker.update_trade(buy_id, 100, candle_high=101, candle_low=100)
assert trade["status"] == "WIN", trade
assert trade.get("result_reason") == "TP1_PROTECTED_WIN", trade
assert trade["exit_price"] == 100, trade
assert trade.get("tp2_hit") is not True, trade
assert trade.get("breakeven_notified") is False, trade
assert trade.get("tp2_notified") is False, trade

# Verify persisted state.
saved = next(t for t in tracker.get_all_trades() if t["trade_id"] == buy_id)
assert saved["status"] == "WIN"
assert saved.get("result_reason") == "TP1_PROTECTED_WIN"
assert saved["exit_price"] == 100

# SELL: entry -> TP1 -> return to entry.
sell_id = create_trade("TEST_SELL_PROTECTED", "SELL", 100, 105, 95, 90)

trade = tracker.update_trade(sell_id, 100, candle_high=101, candle_low=100)
assert trade["status"] == "OPEN", trade

trade = tracker.update_trade(sell_id, 95, candle_high=99, candle_low=94)
assert trade["tp1_hit"] is True, trade
assert trade["stop_loss"] == 100, trade

trade = tracker.update_trade(sell_id, 100, candle_high=100, candle_low=99)
assert trade["status"] == "WIN", trade
assert trade.get("result_reason") == "TP1_PROTECTED_WIN", trade
assert trade["exit_price"] == 100, trade

# Ordinary BUY stop loss before TP1 must remain a LOSS.
loss_id = create_trade("TEST_BUY_LOSS", "BUY", 100, 95, 105, 110)

trade = tracker.update_trade(loss_id, 100, candle_high=100, candle_low=99)
assert trade["status"] == "OPEN", trade

trade = tracker.update_trade(loss_id, 94, candle_high=99, candle_low=94)
assert trade["status"] == "LOSS", trade
assert trade.get("result_reason") != "TP1_PROTECTED_WIN", trade

print("PASS: BUY TP1 -> entry return is WIN")
print("PASS: SELL TP1 -> entry return is WIN")
print("PASS: Protected-win result persists")
print("PASS: Protected win does not set TP2/BE notification flags")
print("PASS: Ordinary pre-TP1 stop remains LOSS")
print("ALL TP1 PROTECTED-WIN REGRESSION TESTS PASSED")
