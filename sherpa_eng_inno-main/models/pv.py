"""PV model: output per kWp, hourly.

Simplification (day 1): GHI is used as plane-of-array irradiance
(no tilt model). Replace later by PVGIS plane-of-array data if available.
"""
from __future__ import annotations

import numpy as np


def pv_power_per_kwp(
    ghi_wm2,
    t_amb_c,
    noct: float = 45.0,
    gamma: float = -0.004,
    eta_sys: float = 0.86,
):
    """Return AC power in kW per kWp installed.

    t_cell = t_amb + (NOCT - 20) / 800 * G
    P = (G / 1000) * (1 + gamma * (t_cell - 25)) * eta_sys
    """
    ghi = np.asarray(ghi_wm2, dtype=float)
    t_amb = np.asarray(t_amb_c, dtype=float)
    t_cell = t_amb + (noct - 20.0) / 800.0 * ghi
    p = (ghi / 1000.0) * (1.0 + gamma * (t_cell - 25.0)) * eta_sys
    return np.clip(p, 0.0, None)
