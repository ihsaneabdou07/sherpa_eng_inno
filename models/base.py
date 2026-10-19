"""Common conventions for all models.

Every model module exposes:
    simulate(inputs: pd.DataFrame, params: dict) -> pd.DataFrame
Inputs and outputs are hourly (8760 rows), units kW / kWh / kg / m3.
"""
from __future__ import annotations

import pandas as pd

HOURS = 8760
WEATHER_COLUMNS = ["timestamp_utc", "ghi_wm2", "t2m_c", "ws100_ms"]


def check_hourly(df: pd.DataFrame, name: str = "inputs") -> None:
    """Raise ValueError if df is not a clean 8760-row hourly table."""
    if len(df) != HOURS:
        raise ValueError(f"{name}: expected {HOURS} rows, got {len(df)}")
    if df.isna().any().any():
        raise ValueError(f"{name}: contains missing values")
