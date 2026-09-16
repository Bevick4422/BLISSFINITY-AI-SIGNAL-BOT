
from pathlib import Path

path = Path("tracking/trade_tracker.py")
text = path.read_text(encoding="utf-8")

start_marker = "# =====================================================\n# TRADE UPDATE\n# =====================================================\n"
end_marker = "# =====================================================\n# PERFORMANCE\n# ====================================================="

start = text.index(start_marker)
end = text.index(end_marker, start)

new_section = '''# =====================================================
# TRADE UPDATE
# =====================================================

def update_trade(
    trade_id: str,
    current_price: float,
    candle_high: float | None = None,
    candle_low: float | None = None,
) -> dict[str, Any] | None:
    """
    Update one trade using the latest market price and,
    when available, the completed candle range.

    Candle high/low allow the tracker to detect TP/SL
    levels that were touched between polling cycles.
    """

    trades = _load_trades()

    for trade in trades:
        if trade.get("trade_id") != trade_id:
            continue

        status = _normalise_status(trade)

        if status in {
            "WIN",
            "LOSS",
            "BREAKEVEN",
        }:
            return trade

        entry = float(trade["entry"])
        stop_loss = float(trade["stop_loss"])
        tp1 = float(trade["tp1"])
        tp2 = float(trade["tp2"])

        price = float(current_price)
        direction = str(
            trade["direction"]
        ).upper()

        high = (
            float(candle_high)
            if candle_high is not None
            else price
        )

        low = (
            float(candle_low)
            if candle_low is not None
            else price
        )

        # -------------------------------------------------
        # PENDING -> OPEN
        # -------------------------------------------------

        if status == "PENDING":

            reached_entry = (
                high >= entry
                if direction == "BUY"
                else low <= entry
            )

            if not reached_entry:
                return trade

            now = _now()

            trade["status"] = "OPEN"
            trade["state"] = "OPEN"
            trade["opened_at"] = now
            trade["updated_at"] = now

            _add_event(
                trade,
                "ENTRY_REACHED",
                entry,
            )

            status = "OPEN"

        # -------------------------------------------------
        # OPEN TRADE MANAGEMENT
        # -------------------------------------------------

        if status == "OPEN":

            if direction == "BUY":

                stopped = low <= stop_loss
                reached_tp1 = high >= tp1
                reached_tp2 = high >= tp2

            else:

                stopped = high >= stop_loss
                reached_tp1 = low <= tp1
                reached_tp2 = low <= tp2

            # -------------------------------------------------
            # STOP LOSS
            # -------------------------------------------------

            if stopped:

                if trade.get("break_even"):
                    _close_trade(
                        trade,
                        "BREAKEVEN",
                        entry,
                    )
                else:
                    _close_trade(
                        trade,
                        "LOSS",
                        stop_loss,
                    )

            # -------------------------------------------------
            # TP2
            # -------------------------------------------------

            elif reached_tp2:

                _close_trade(
                    trade,
                    "WIN",
                    tp2,
                )

            # -------------------------------------------------
            # TP1
            # -------------------------------------------------

            elif (
                reached_tp1
                and not trade.get("tp1_hit")
            ):

                trade["tp1_hit"] = True
                trade["break_even"] = True
                trade["stop_loss"] = entry
                trade["status"] = "OPEN"
                trade["state"] = "BREAK_EVEN"
                trade["updated_at"] = _now()

                _add_event(
                    trade,
                    "TP1_REACHED",
                    tp1,
                )

                _add_event(
                    trade,
                    "STOP_MOVED_TO_ENTRY",
                    entry,
                )

        trade["updated_at"] = _now()

        _save_trades(trades)

        return trade

    return None


'''

path.write_text(
    text[:start] + new_section + text[end:],
    encoding="utf-8",
)

