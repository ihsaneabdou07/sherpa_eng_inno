"""tests/test_hourly_sim.py"""
import numpy as np
from economics.hourly_sim import (SimConfig, synthetic_profiles, simulate, effective_electricity_price,
                                  sweep_re_ratio, monthly_summary, cost_with_simulation, HOURS)
from economics.efuel_economics import Params


def test_profiles_shape_and_targets():
    pv, wd = synthetic_profiles(0.30, 0.45)
    assert len(pv) == len(wd) == HOURS
    assert abs(pv.mean() - 0.30) < 0.005 and abs(wd.mean() - 0.45) < 0.01
    assert pv.min() >= 0 and pv.max() <= 1 and wd.min() >= 0 and wd.max() <= 1
    assert pv[:5].sum() == 0              # nuit (hiver, minuit-4h) : pas de PV


def test_energy_balance():
    pv, wd = synthetic_profiles()
    s = simulate(SimConfig(), pv, wd)
    assert abs(s["supply_mwh"] - s["used_mwh"] - s["curtailed_mwh"]) < 1e-6


def test_flh_increases_with_oversizing_and_price_effective_rises():
    pv, wd = synthetic_profiles()
    rows = sweep_re_ratio(SimConfig(), pv, wd)
    flh = [r["flh"] for r in rows]; px = [r["prix_effectif_eur_mwh"] for r in rows]
    assert all(b >= a - 1e-9 for a, b in zip(flh, flh[1:]))
    assert px[-1] > px[0]                 # l'énergie écrêtée est payée


def test_battery_does_not_reduce_flh():
    pv, wd = synthetic_profiles()
    a = simulate(SimConfig(), pv, wd)["flh"]
    b = simulate(SimConfig(battery_mwh=500, battery_mw=100), pv, wd)["flh"]
    assert b >= a - 1e-9


def test_monthly_sums_match_total():
    pv, wd = synthetic_profiles()
    s = simulate(SimConfig(), pv, wd)
    assert abs(sum(m["used_mwh"] for m in monthly_summary(s)) - s["used_mwh"]) < 1e-6


def test_min_load_blocks_low_power_hours():
    pv = np.full(HOURS, 0.02); wd = np.zeros(HOURS)       # 6 MW pour 300 MW PV < 10 % de 250 MW
    s = simulate(SimConfig(pv_mw=300, wind_mw=0, electrolyser_mw=250, min_load=0.10), pv, wd)
    assert s["used_mwh"] == 0 and s["hours_running"] == 0


def test_cost_with_simulation_runs():
    pv, wd = synthetic_profiles()
    s = simulate(SimConfig(), pv, wd)
    c = cost_with_simulation(s, "e-methanol", Params())
    assert c["total_eur_t"] > 0
