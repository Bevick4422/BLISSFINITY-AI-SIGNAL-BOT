import pandas as pd
import numpy as np

from analysis.market_structure.market_structure_engine import detect_market_structure

df = pd.DataFrame({
    "high": np.linspace(100,110,20),
    "low": np.linspace(90,100,20)
})

print("="*50)
print("MARKET STRUCTURE TEST")
print("="*50)

print(detect_market_structure(df))
