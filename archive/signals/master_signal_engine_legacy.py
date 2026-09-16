from signals.ai_signal_engine import generate_signal
from signals.smart_risk_manager import build_trade


def build_master_signal(df, symbol="UNKNOWN"):
    signal = generate_signal(df, symbol)

    if signal is None:
        return None

    trade = build_trade(
        direction=signal["direction"],
        entry=signal["entry"],
        structure_high=signal["structure_high"],
        structure_low=signal["structure_low"],
        demand_zone=signal["demand_zone"],
        supply_zone=signal["supply_zone"],
    )

    if trade is None:
        return None

    signal.update(trade)

    return signal
