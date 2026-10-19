import numpy as np
import pytest

from models.electrolyzer import hydrogen_kg_per_h


def test_one_mwh_gives_about_19_kg():
    assert float(hydrogen_kg_per_h(1000.0, 1000.0, 52.5)) == pytest.approx(19.05, abs=0.01)


def test_below_min_load_is_off():
    assert float(hydrogen_kg_per_h(50.0, 1000.0, 52.5, min_load=0.10)) == 0.0


def test_capped_at_nominal():
    out = hydrogen_kg_per_h(np.array([2000.0]), 1000.0, 52.5)
    assert float(out[0]) == pytest.approx(1000.0 / 52.5)
