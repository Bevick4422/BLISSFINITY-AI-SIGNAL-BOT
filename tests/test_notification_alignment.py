from __future__ import annotations

import ast
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_tracker():
    spec = importlib.util.spec_from_file_location(
        "isolated_trade_tracker", ROOT / "tracking" / "trade_tracker.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_single_tp_closes_as_win_and_uses_tp1_compatibility(tmp_path):
    tracker = load_tracker()
    tracker.TRADE_FILE = tmp_path / "trades.json"

    trade_id = tracker.record_signal({
        "symbol": "BTC/USDT",
        "direction": "BUY",
        "entry": 100.0,
        "stop_loss": 90.0,
        "tp1": 120.0,
        "tp2": 130.0,
        "risk": 10.0,
        "rr": 2.0,
    })
    assert trade_id

    # First completed candle reaches entry; target checks wait for next candle.
    trade = tracker.update_trade(
        trade_id, 100.0, candle_high=100.0, candle_low=99.0,
        candle_timestamp=1,
    )
    assert trade["status"] == "OPEN"

    trade = tracker.update_trade(
        trade_id, 120.0, candle_high=121.0, candle_low=100.0,
        candle_timestamp=2,
    )
    assert trade["status"] == "WIN"
    assert trade["exit_price"] == 120.0
    assert trade["r_multiple"] == 2.0
    assert trade["tp"] == 120.0


def test_one_r_moves_stop_to_entry_without_tp_notification_state(tmp_path):
    tracker = load_tracker()
    tracker.TRADE_FILE = tmp_path / "trades.json"

    trade_id = tracker.record_signal({
        "symbol": "ETH/USDT",
        "direction": "BUY",
        "entry": 100.0,
        "stop_loss": 90.0,
        "tp1": 120.0,
        "tp2": 130.0,
        "risk": 10.0,
    })
    tracker.update_trade(
        trade_id, 100.0, candle_high=100.0, candle_low=99.0,
        candle_timestamp=1,
    )
    trade = tracker.update_trade(
        trade_id, 110.0, candle_high=110.0, candle_low=101.0,
        candle_timestamp=2,
    )
    assert trade["status"] == "OPEN"
    assert trade["break_even"] is True
    assert trade["stop_loss"] == 100.0
    assert trade["tp_notified"] is False


def test_main_has_single_tp_sender_and_no_tp1_tp2_send_paths():
    tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
    calls = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "send_tp_hit" in calls
    assert "send_tp1_hit" not in calls
    assert "send_tp2_hit" not in calls


def test_formatter_has_single_take_profit_label():
    text = (ROOT / "telegram" / "formatter.py").read_text(encoding="utf-8")
    assert "Take Profit 1" not in text
    assert "Take Profit 2" not in text
    assert "TAKE PROFIT HIT" in text


def test_weekly_report_joins_lines_with_real_newlines():
    text = (ROOT / "telegram" / "sender.py").read_text(encoding="utf-8")
    assert 'send_message("\\n".join(lines))' in text
    assert 'send_message("\\\\n".join(lines))' not in text


def test_new_trade_uses_single_tp_schema_and_no_tp1_hit_flag(tmp_path):
    tracker = load_tracker()
    tracker.TRADE_FILE = tmp_path / "trades.json"

    trade_id = tracker.record_signal({
        "symbol": "SOL/USDT",
        "direction": "BUY",
        "entry": 100.0,
        "stop_loss": 90.0,
        "tp1": 120.0,
        "tp2": 130.0,
        "risk": 10.0,
    })
    trade = next(t for t in tracker._load_trades() if t["trade_id"] == trade_id)
    assert trade["tp"] == 120.0
    assert "tp1_hit" not in trade
    assert "tp1" not in trade
    assert "tp2" not in trade


def test_protected_return_to_entry_is_recorded_as_breakeven(tmp_path):
    tracker = load_tracker()
    tracker.TRADE_FILE = tmp_path / "trades.json"

    trade_id = tracker.record_signal({
        "symbol": "ETH/USDT",
        "direction": "BUY",
        "entry": 100.0,
        "stop_loss": 90.0,
        "tp1": 120.0,
        "tp2": 130.0,
        "risk": 10.0,
    })
    tracker.update_trade(
        trade_id, 100.0, candle_high=100.0, candle_low=99.0,
        candle_timestamp=1,
    )
    protected = tracker.update_trade(
        trade_id, 110.0, candle_high=110.0, candle_low=101.0,
        candle_timestamp=2,
    )
    assert protected["status"] == "OPEN"
    assert protected["original_stop_loss"] == 90.0

    closed = tracker.update_trade(
        trade_id, 100.0, candle_high=101.0, candle_low=100.0,
        candle_timestamp=3,
    )
    assert closed["status"] == "BREAKEVEN"
    assert closed["result_reason"] == "PROTECTED_RETURN_TO_ENTRY"


def test_monitor_contains_only_one_tp_notification_call():
    tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
    monitor = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "monitor_active_trades"
    )
    calls = [
        node for node in ast.walk(monitor)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "send_tp_hit"
    ]
    assert len(calls) == 1
