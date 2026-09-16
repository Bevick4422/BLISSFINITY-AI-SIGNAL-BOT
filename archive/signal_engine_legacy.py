
"""
BLISSFINITY AI SIGNAL BOT
MASTER SIGNAL ENGINE
"""

from scanner.market_scanner import fetch_market_data

# Weekly
from analysis.weekly_bias.weekly_bias_engine import detect_weekly_bias

# Daily
from analysis.daily_structure.daily_structure_engine import detect_daily_structure
from analysis.daily_bos.daily_bos_engine import detect_daily_bos

# H4
from analysis.h4_structure.h4_structure_engine import detect_h4_structure
from analysis.h4_bos.h4_bos_engine import detect_h4_bos

# Entry
from analysis.key_levels.key_level_engine import detect_key_levels
from analysis.fresh_levels.fresh_level_engine import detect_fresh_levels
from analysis.left_shoulder.left_shoulder_engine import detect_left_shoulder
from analysis.inducement.inducement_engine import detect_inducement
from analysis.supply_demand.supply_demand_engine import detect_supply_demand
from analysis.entry_engine.entry_engine import detect_entry

# Liquidity
from analysis.institutional_liquidity.institutional_liquidity_engine import (
    detect_institutional_liquidity,
)

# Risk
from analysis.risk.risk_engine import calculate_risk

# Rule Engine
from analysis.decision.decision_engine import make_decision

# Confidence
from analysis.confidence.confidence_engine import calculate_confidence


def generate_signal(symbol):
    """
    Complete institutional signal workflow.
    """

    # ==================================================
    # FETCH MARKET DATA
    # ==================================================

    market = fetch_market_data(symbol)

    weekly_df = market["1w"]
    daily_df = market["1d"]
    h4_df = market["4h"]
    m15_df = market["15m"]

    # ==================================================
    # WEEKLY ANALYSIS
    # ==================================================

    weekly = detect_weekly_bias(weekly_df)

    # ==================================================
    # DAILY ANALYSIS
    # ==================================================

    daily_structure = detect_daily_structure(daily_df)
    daily_bos = detect_daily_bos(daily_df)

    # ==================================================
    # H4 ANALYSIS
    # ==================================================

    h4_structure = detect_h4_structure(h4_df)
    h4_bos = detect_h4_bos(h4_df)

    # ==================================================
    # ENTRY ANALYSIS
    # ==================================================

    key_levels = detect_key_levels(m15_df)

    fresh_levels = detect_fresh_levels(
        m15_df,
        key_levels,
    )

    shoulder = detect_left_shoulder(m15_df)

    inducement = detect_inducement(m15_df)

    supply_demand = detect_supply_demand(m15_df)

    entry = detect_entry(
        fresh_levels,
        shoulder,
        inducement,
        supply_demand,
    )

    # ==================================================
    # LIQUIDITY
    # ==================================================

    liquidity = detect_institutional_liquidity(m15_df)

    # ==================================================
    # RISK MANAGEMENT
    # ==================================================

    current_price = float(m15_df["close"].iloc[-1])

    atr = (
        (m15_df["high"] - m15_df["low"])
        .rolling(14)
        .mean()
        .iloc[-1]
    )

    if atr is None or atr != atr:
        atr = current_price * 0.005

    risk = calculate_risk(
        entry=current_price,
        atr=atr,
        direction=weekly["bias"],
        rr=3,
    )

    # ==================================================
    # RULE ENGINE
    # ==================================================

    decision = make_decision(
        weekly,
        daily_structure,
        daily_bos,
        h4_structure,
        h4_bos,
        liquidity,
        entry,
        risk,
    )

    # ==================================================
    # SCAN REPORT
    # ==================================================

    print(f"""
========================================================
PAIR            : {symbol}

Weekly Bias     : {weekly['bias']}
Daily Trend     : {daily_structure['trend']}
Daily BOS       : {daily_bos['bos']}
H4 Trend        : {h4_structure['trend']}
H4 BOS          : {h4_bos['bos']}
Liquidity Sweep : {liquidity['liquidity_grab']}
Entry Trigger   : {entry['approved']}
Risk Reward     : 1:{risk['rr']}

Approved        : {decision['approved']}
Direction       : {decision['direction']}

Reasons
--------------------------------------------------------
{chr(10).join('- ' + r for r in decision['reasons']) if decision['reasons'] else 'Trade Approved'}

========================================================
""")

    if not decision["approved"]:
        return None

    # ==================================================
    # CONFIDENCE
    # ==================================================

    confidence = calculate_confidence(
        weekly,
        daily_structure,
        daily_bos,
        h4_structure,
        h4_bos,
        liquidity,
        entry,
        risk,
    )

    # ==================================================
    # FINAL SIGNAL
    # ==================================================

    signal = {

        "pair": symbol,

        "side": decision["direction"],

        "entry": risk["entry"],

        "stop_loss": risk["stop_loss"],

        "tp1": risk["tp1"],

        "tp2": risk["tp2"],

        "rr": risk["rr"],

        "confidence": confidence["score"],

        "grade": confidence["grade"],

        "score": confidence["score"],

        "reasons": confidence["reasons"],

    }

    return signal