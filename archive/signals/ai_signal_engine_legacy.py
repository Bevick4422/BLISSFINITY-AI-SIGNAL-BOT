"""
BLISSFINITY AI SIGNAL ENGINE
Final Version
"""

from analysis.market_structure.market_structure_engine import detect_market_structure
from analysis.liquidity.liquidity_engine import detect_liquidity_grab
from analysis.supply_demand.supply_demand_engine import detect_supply_demand
from analysis.fvg.fvg_engine import detect_fvg
from analysis.order_blocks.order_block_engine import detect_order_block
from analysis.volume.volume_engine import analyze_volume
from analysis.momentum.momentum_engine import analyze_momentum
from analysis.atr.atr_engine import calculate_atr
from analysis.multi_timeframe.mtf_engine import confirm_multi_timeframe
from analysis.premium_discount.premium_discount_engine import detect_premium_discount
from analysis.session.session_engine import session_bias

from signals.smart_risk_manager import build_trade


def generate_signal(df, symbol="UNKNOWN"):

    if df is None or len(df) < 50:
        return None

    # ------------------------------------
    # ANALYSIS
    # ------------------------------------

    structure = detect_market_structure(df)

    liquidity = detect_liquidity_grab(df)

    supply_demand = detect_supply_demand(df)

    fvg = detect_fvg(df)

    order_block = detect_order_block(df)

    volume = analyze_volume(df)

    momentum = analyze_momentum(df)

    premium_discount = detect_premium_discount(df)

    session = session_bias()

    atr = calculate_atr(df)

    mtf = confirm_multi_timeframe(
        weekly_bias="BUY",
        daily_bias=structure.get("signal"),
        h4_bias=momentum.get("momentum"),
    )

    # ------------------------------------
    # DIRECTION
    # ------------------------------------

    direction = None

    signal = structure.get("signal")

    if signal == "BOS_BULLISH":
        direction = "BUY"

    elif signal == "BOS_BEARISH":
        direction = "SELL"

    if direction is None:
        return None

    # ------------------------------------
    # SCORE
    # ------------------------------------

    score = 20

    if direction == "BUY":

        if liquidity.get("liquidity_sweep_low"):
            score += 10

        if supply_demand.get("bias") == "BUY":
            score += 10

        if fvg.get("type") == "BULLISH":
            score += 10

        if order_block.get("type") == "BULLISH":
            score += 10

        if momentum.get("momentum") == "BULLISH":
            score += 10

        if premium_discount.get("zone") == "DISCOUNT":
            score += 10

    else:

        if liquidity.get("liquidity_sweep_high"):
            score += 10

        if supply_demand.get("bias") == "SELL":
            score += 10

        if fvg.get("type") == "BEARISH":
            score += 10

        if order_block.get("type") == "BEARISH":
            score += 10

        if momentum.get("momentum") == "BEARISH":
            score += 10

        if premium_discount.get("zone") == "PREMIUM":
            score += 10

    if volume.get("volume_signal") == "HIGH":
        score += 5

    if session["strength"] >= 80:
        score += 10

    elif session["strength"] >= 40:
        score += 5

    if mtf.get("confirmed"):
        score += 15

    if score < 70:
        return None

    # ------------------------------------
    # BUILD TRADE
    # ------------------------------------

    entry = float(df["close"].iloc[-1])

    trade = build_trade(
        direction=direction,
        entry=entry,
        structure_high=float(df["high"].tail(20).max()),
        structure_low=float(df["low"].tail(20).min()),
    )

    # ------------------------------------
    # FINAL SIGNAL
    # ------------------------------------

    return {

        "pair": symbol,

        "direction": direction,

        "entry": trade["entry"],

        "stop": trade["stop"],

        "tp1": trade["tp1"],

        "tp2": trade["tp2"],

        "rr": trade["rr"],

        "confidence": score,

        "atr": atr,

        "market_structure": structure,

        "liquidity": liquidity,

        "supply_demand": supply_demand,

        "fvg": fvg,

        "order_block": order_block,

        "volume": volume,

        "momentum": momentum,

        "premium_discount": premium_discount,

        "session": session,

        "multi_timeframe": mtf,
    }
