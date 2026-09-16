from analysis.multi_timeframe.mtf_engine import confirm_multi_timeframe

print("=" * 50)
print("MULTI TIMEFRAME TEST")
print("=" * 50)

result = confirm_multi_timeframe(
    "BUY",
    "BUY",
    "BUY"
)

print(result)

assert result["confirmed"] is True
assert result["direction"] == "BUY"

print("\nSUCCESS")
