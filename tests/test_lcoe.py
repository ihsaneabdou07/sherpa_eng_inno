import pytest

from economics.lcoe import annualized_cost, crf, lcoe


def test_crf_known_value():
    assert crf(0.08, 20) == pytest.approx(0.101852, abs=1e-6)


def test_crf_zero_rate():
    assert crf(0.0, 10) == pytest.approx(0.1)


def test_annualized_cost():
    assert annualized_cost(1000.0, 0.02, 0.08, 20) == pytest.approx(121.852, abs=1e-3)


def test_lcoe():
    assert lcoe(100.0, 1000.0) == pytest.approx(0.1)
