import pandas as pd

from signals.ai_signal_engine import generate_signal

print("="*50)
print("AI SIGNAL ENGINE TEST")
print("="*50)

df = pd.DataFrame({
    "open":[i for i in range(100)],
    "high":[i+1 for i in range(100)],
    "low":[i-1 for i in range(100)],
    "close":[i for i in range(100)],
    "volume":[5000]*100
})

result = generate_signal(df)

print(result)

print("\nSUCCESS")
