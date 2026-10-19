import pytest

from models.wind import extrapolate_wind, wind_power_per_kw


def test_zero_below_cut_in():
    assert float(wind_power_per_kw(2.0)) == 0.0


def test_rated_with_losses():
    assert float(wind_power_per_kw(15.0, losses=0.12)) == pytest.approx(0.88)


def test_zero_above_cut_out():
    assert float(wind_power_per_kw(30.0)) == 0.0


def test_extrapolation_identity_at_same_height():
    assert float(extrapolate_wind(8.0, 100, 100)) == pytest.approx(8.0)
