import numpy as np
import pytest

from models.pv import pv_power_per_kwp


def test_zero_at_night():
    assert np.all(pv_power_per_kwp(np.zeros(24), np.full(24, 20.0)) == 0.0)


def test_stc_equals_system_efficiency():
    # t_amb chosen so that t_cell = 25 C at G = 1000 W/m2: 25 - (45-20)/800*1000
    p = pv_power_per_kwp(1000.0, 25.0 - 25.0 / 800.0 * 1000.0)
    assert float(p) == pytest.approx(0.86)


def test_never_negative_or_above_one():
    g = np.linspace(0, 1200, 50)
    p = pv_power_per_kwp(g, np.full(50, 30.0))
    assert p.min() >= 0.0 and p.max() <= 1.0
