"""Create a synthetic weather file (8760 h) to develop models before real data."""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
idx = pd.date_range("2021-01-01", periods=8760, freq="h", tz="UTC")  # 2021: not a leap year
hour = idx.hour.to_numpy()

ghi = np.clip(1000.0 * np.sin(np.pi * (hour - 6) / 12.0), 0.0, None)  # sunrise 6h, sunset 18h
t2m = 22.0 + 6.0 * np.sin(2.0 * np.pi * (hour - 9) / 24.0)
ws100 = np.clip(rng.weibull(2.2, size=8760) * 9.0, 0.0, 40.0)

df = pd.DataFrame({"timestamp_utc": idx, "ghi_wm2": ghi, "t2m_c": t2m, "ws100_ms": ws100})
out = Path("data/processed/synthetic_site.csv")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f"written {out} ({len(df)} rows)")
