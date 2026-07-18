from analysis.confluence.confluence_engine import calculate_confluence

print("=" * 50)
print("CONFLUENCE ENGINE TEST")
print("=" * 50)

trend = {
    "trend": "BULLISH"
}

structure = {
    "bos": True
}

liquidity = {
    "sweep": True
}

smc = {
    "bullish_order_block": True,
    "bearish_order_block": False,
    "bullish_fvg": True,
    "bearish_fvg": False
}

wave = {
    "wave": "IMPULSE"
}

momentum = {
    "momentum": "BULLISH"
}

result = calculate_confluence(
    trend,
    structure,
    liquidity,
    smc,
    wave,
    momentum
)

print(result)

assert "score" in result
assert "signal" in result

print("\nSUCCESS")
