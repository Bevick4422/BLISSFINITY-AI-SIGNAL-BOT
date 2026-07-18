from analysis.risk.risk_engine import calculate_trade

print("=" * 50)
print("RISK ENGINE TEST")
print("=" * 50)

trade = calculate_trade(

    entry=1.2500,
    atr=0.0100,
    direction="BUY"

)

print(trade)

assert "entry" in trade
assert "stop_loss" in trade
assert "take_profit" in trade
assert trade["rr"] >= 3

print("\nSUCCESS")
