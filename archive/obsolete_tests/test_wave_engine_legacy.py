import pandas as pd

from analysis.wave.wave_engine import detect_wave

print("=" * 50)
print("WAVE ENGINE TEST")
print("=" * 50)

df = pd.DataFrame({
    "high":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
    "low":[1]*20
})

result = detect_wave(df)

print(result)

assert "wave" in result

print("\nSUCCESS")
