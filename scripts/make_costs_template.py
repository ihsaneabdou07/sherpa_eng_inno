"""Create the empty cost table (CSV + XLSX). Fill it with sourced values."""
from pathlib import Path

import pandas as pd

COLUMNS = [
    "component", "capex", "unit", "opex_pct_capex_per_year", "lifetime_years",
    "low", "central", "high", "currency", "currency_year", "source_1", "source_2", "notes",
]
COMPONENTS = [
    ("pv", "EUR/kWp"), ("wind", "EUR/kW"), ("battery", "EUR/kWh"),
    ("electrolyzer", "EUR/kW"), ("h2_storage", "EUR/kg"), ("h2_compression", "EUR/kW"),
    ("desalination", "EUR/(m3/day)"), ("ammonia_synthesis", "EUR/(t/day)"),
]
rows = [{"component": c, "unit": u, "currency": "EUR", "currency_year": 2024} for c, u in COMPONENTS]
df = pd.DataFrame(rows, columns=COLUMNS)
Path("data").mkdir(exist_ok=True)
df.to_csv("data/costs_template.csv", index=False)
df.to_excel("data/costs.xlsx", index=False)
print("written data/costs_template.csv and data/costs.xlsx")
