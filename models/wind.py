"""Wind model: output per kW of rated power, hourly."""
from __future__ import annotations

import numpy as np


def extrapolate_wind(v_ref, h_ref: float = 100.0, h_hub: float = 100.0, alpha: float = 0.14):
    """Power-law extrapolation: v_h = v_ref * (h_hub / h_ref) ** alpha."""
    return np.asarray(v_ref, dtype=float) * (h_hub / h_ref) ** alpha


def wind_power_per_kw(
    v_hub,
    v_cut_in: float = 3.0,
    v_rated: float = 12.0,
    v_cut_out: float = 25.0,
    losses: float = 0.12,
):
    """Return power in kW per kW rated.

    0 below cut-in, cubic rise to rated, 1 until cut-out, 0 above.
    Global losses (wake, availability, electrical) applied at the end.
    """
    v = np.asarray(v_hub, dtype=float)
    ramp = (v**3 - v_cut_in**3) / (v_rated**3 - v_cut_in**3)
    p = np.where(v < v_cut_in, 0.0, np.where(v < v_rated, ramp, 1.0))
    p = np.where(v >= v_cut_out, 0.0, p)
    return p * (1.0 - losses)
