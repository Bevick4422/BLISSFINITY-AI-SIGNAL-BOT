from signals.smart_risk_manager import build_trade

trade = build_trade(

    direction="BUY",

    entry=109230,

    structure_high=111000,

    structure_low=108500,

    demand_zone=108700,

)

print("=" * 50)
print("SMART RISK TEST")
print("=" * 50)

print(trade)

print("\nSUCCESS")
