"""Electrolyzer model (day 1 skeleton, completed on day 3)."""
from __future__ import annotations

import numpy as np


def hydrogen_kg_per_h(
    power_kw,
    p_nom_kw: float,
    sec_kwh_per_kg: float = 52.5,
    min_load: float = 0.10,
):
    """Hydrogen production in kg/h for an hourly input power in kW.

    - power is capped at the nominal power
    - below min_load * p_nom the stack is off (no production)
    """
    p = np.minimum(np.asarray(power_kw, dtype=float), p_nom_kw)
    p = np.where(p >= min_load * p_nom_kw, p, 0.0)
    return p / sec_kwh_per_kg
