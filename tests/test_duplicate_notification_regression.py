import asyncio
import ast
from pathlib import Path

import main


def test_win_notification_is_not_retried_after_success(monkeypatch):
    trade = {
        "trade_id": "duplicate-test-win",
        "status": "WIN",
        "entry_notified": True,
        "tp_notified": False,
        "tp2_notified": False,
    }
    sent_events = []

    async def fake_send_tp_hit(current_trade):
        sent_events.append(current_trade["trade_id"])
        return True

    def fake_get_all_trades():
        # Simulate reloading persisted trade state on every retry.
        return [dict(trade)]

    def fake_mark_notification_sent(trade_id, key):
        assert trade_id == trade["trade_id"]
        trade[key] = True
        return True

    monkeypatch.setattr(main, "get_all_trades", fake_get_all_trades)
    monkeypatch.setattr(main, "send_tp_hit", fake_send_tp_hit)
    monkeypatch.setattr(
        main, "mark_notification_sent", fake_mark_notification_sent
    )

    async def scenario():
        await main.retry_pending_notifications()
        await main.retry_pending_notifications()

    asyncio.run(scenario())

    assert sent_events == ["duplicate-test-win"]
    assert trade["tp_notified"] is True


def test_legacy_tp2_flag_prevents_duplicate_tp(monkeypatch):
    trade = {
        "trade_id": "duplicate-test-legacy",
        "status": "WIN",
        "entry_notified": True,
        "tp_notified": False,
        "tp2_notified": True,
    }
    sent_events = []

    async def fake_send_tp_hit(current_trade):
        sent_events.append(current_trade["trade_id"])
        return True

    monkeypatch.setattr(main, "get_all_trades", lambda: [dict(trade)])
    monkeypatch.setattr(main, "send_tp_hit", fake_send_tp_hit)

    asyncio.run(main.retry_pending_notifications())

    assert sent_events == []


def test_monitor_has_only_one_final_tp_sender_call():
    source = (Path(__file__).resolve().parents[1] / "main.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
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
