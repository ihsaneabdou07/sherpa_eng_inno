"""
hourly_sim.py — economics/hourly_sim.py
Simulation horaire PV + éolien -> électrolyseur (heures pleine charge réelles, écrêtage,
stockage batterie optionnel) et couplage au modèle de coût efuel_economics.

IMPORTANT : sans données mesurées, les profils sont SYNTHÉTIQUES (générés avec une
graine fixe, cibles de facteur de charge réglables). Ils servent à illustrer la
méthode et à faire des études de sensibilité. Pour une décision d'investissement,
remplacer par des séries horaires réelles du site (mât de mesure, ERA5,
Renewables.ninja, PVGIS) via load_profiles_csv().

Format CSV attendu (8760 lignes, séparateur ; ou ,) : colonnes pv_cf, wind_cf (0-1).
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

HOURS = 8760
DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def month_index() -> np.ndarray:
    """Mois (1-12) de chaque heure d'une année de 8760 h."""
    m = []
    for i, d in enumerate(DAYS_IN_MONTH, start=1):
        m += [i] * (d * 24)
    return np.array(m)


# ---------------------------------------------------------------- profils synthétiques
def _scale_to_cf(raw: np.ndarray, target_cf: float) -> np.ndarray:
    """Met à l'échelle un profil (puis écrête à 1) pour atteindre un facteur de charge cible."""
    lo, hi = 0.0, 50.0
    for _ in range(60):
        mid = (lo + hi) / 2
        cf = np.clip(raw * mid, 0, 1).mean()
        if cf < target_cf:
            lo = mid
        else:
            hi = mid
    return np.clip(raw * (lo + hi) / 2, 0, 1)


def synthetic_pv(cf: float = 0.30, latitude: float = 28.0, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.arange(HOURS)
    day, hod = t // 24, t % 24
    decl = np.radians(23.45) * np.sin(2 * np.pi * (284 + day) / 365)
    hour_angle = np.radians(15 * (hod + 0.5 - 12))
    lat = np.radians(latitude)
    sin_elev = np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(hour_angle)
    clear = np.clip(sin_elev, 0, None) ** 1.15
    k_day = np.clip(rng.normal(0.88, 0.12, 365), 0.25, 1.0)          # clarté journalière
    k_hour = np.clip(1 + rng.normal(0, 0.04, HOURS), 0.8, 1.1)
    raw = clear * k_day[day] * k_hour
    return _scale_to_cf(raw, cf)


def _norm_cdf(x: np.ndarray) -> np.ndarray:
    return 0.5 * (1 + np.array([math.erf(v / math.sqrt(2)) for v in x]))


def _power_curve(v: np.ndarray) -> np.ndarray:
    """Courbe de puissance générique (démarrage 3 m/s, nominal 12 m/s, coupure 25 m/s)."""
    p = np.zeros_like(v)
    ramp = (v >= 3) & (v < 12)
    p[ramp] = ((v[ramp] - 3) / 9.0) ** 3
    p[(v >= 12) & (v <= 25)] = 1.0
    return p


def synthetic_wind(cf: float = 0.45, seed: int = 2, k: float = 2.2) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = HOURS
    z = np.zeros(n)
    eps = rng.normal(0, 1, n)
    phi = 0.985                                                    # forte autocorrélation horaire
    for i in range(1, n):
        z[i] = phi * z[i - 1] + math.sqrt(1 - phi ** 2) * eps[i]
    u = np.clip(_norm_cdf(z), 1e-6, 1 - 1e-6)
    t = np.arange(n)
    hod, day = t % 24, t // 24
    diurnal = 1 + 0.12 * np.cos(2 * np.pi * (hod - 16) / 24)        # alizés : maximum en fin d'après-midi
    seasonal = 1 + 0.10 * np.cos(2 * np.pi * (day - 190) / 365)     # maximum en été (côte atlantique)
    unit = (-np.log(1 - u)) ** (1 / k)                              # Weibull(k, 1)
    lo, hi = 2.0, 20.0
    for _ in range(50):
        c = (lo + hi) / 2
        got = _power_curve(c * unit * diurnal * seasonal).mean()
        if got < cf:
            lo = c
        else:
            hi = c
    return _power_curve(((lo + hi) / 2) * unit * diurnal * seasonal)


def synthetic_profiles(pv_cf: float = 0.30, wind_cf: float = 0.45, latitude: float = 28.0,
                       seed: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    return synthetic_pv(pv_cf, latitude, seed), synthetic_wind(wind_cf, seed + 1)


def load_profiles_csv(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Lit un CSV (colonnes pv_cf, wind_cf entre 0 et 1, 8760 lignes)."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048); f.seek(0)
        delim = ";" if sample.count(";") > sample.count(",") else ","
        rows = list(csv.DictReader(f, delimiter=delim))
    pv = np.array([float(r["pv_cf"].replace(",", ".")) for r in rows])
    wd = np.array([float(r["wind_cf"].replace(",", ".")) for r in rows])
    if len(pv) != HOURS or len(wd) != HOURS:
        raise ValueError(f"8760 lignes attendues, reçu {len(pv)}")
    if pv.min() < 0 or pv.max() > 1.0001 or wd.min() < 0 or wd.max() > 1.0001:
        raise ValueError("Les facteurs de charge doivent être compris entre 0 et 1")
    return pv, wd


# ---------------------------------------------------------------- simulation
@dataclass(frozen=True)
class SimConfig:
    pv_mw: float = 300.0
    wind_mw: float = 200.0
    electrolyser_mw: float = 250.0
    min_load: float = 0.10              # fraction de la puissance nominale (PEM : 0-10 % ; AEL ~20 %)
    battery_mwh: float = 0.0
    battery_mw: float = 0.0
    battery_eff: float = 0.90           # rendement aller-retour [HYP]


def simulate(cfg: SimConfig, pv_cf: Sequence[float], wind_cf: Sequence[float]) -> Dict:
    pv = cfg.pv_mw * np.asarray(pv_cf, dtype=float)
    wd = cfg.wind_mw * np.asarray(wind_cf, dtype=float)
    supply = pv + wd
    n = len(supply)
    el = cfg.electrolyser_mw
    min_p = cfg.min_load * el
    used = np.zeros(n)
    curt = np.zeros(n)
    soc = 0.0
    soc_trace = np.zeros(n)
    eta = math.sqrt(cfg.battery_eff)
    for i in range(n):
        direct = min(supply[i], el)
        surplus = supply[i] - direct
        deficit = el - direct
        discharge = 0.0
        if cfg.battery_mwh > 0 and deficit > 0 and soc > 0:
            discharge = min(deficit, cfg.battery_mw, soc * eta)
        if direct + discharge < min_p:          # sous le minimum technique : électrolyseur à l'arrêt
            direct, discharge = 0.0, 0.0
            surplus = supply[i]
        used[i] = direct + discharge
        soc -= discharge / eta
        charge = 0.0
        if cfg.battery_mwh > 0 and surplus > 0:
            charge = min(surplus, cfg.battery_mw, (cfg.battery_mwh - soc) / eta)
            soc += charge * eta
        curt[i] = surplus - charge
        soc_trace[i] = soc
    energy_used = used.sum()
    gen = supply.sum()
    running = used > 1e-9
    starts = int(np.sum(running[1:] & ~running[:-1]) + (1 if running[0] else 0))
    return {
        "supply_mwh": float(gen), "pv_mwh": float(pv.sum()), "wind_mwh": float(wd.sum()),
        "used_mwh": float(energy_used), "curtailed_mwh": float(curt.sum()),
        "flh": float(energy_used / el) if el > 0 else 0.0,
        "curtailment_pct": float(curt.sum() / gen) if gen > 0 else 0.0,
        "re_capacity_factor": gen / ((cfg.pv_mw + cfg.wind_mw) * n) if (cfg.pv_mw + cfg.wind_mw) > 0 else 0.0,
        "hours_running": int(running.sum()),
        "hours_full_load": int(np.sum(used >= el - 1e-9)),
        "starts": starts,
        "used_series": used, "supply_series": supply, "curtailed_series": curt,
        "soc_series": soc_trace,
    }


def effective_electricity_price(sim: Dict, pv_lcoe: float, wind_lcoe: float) -> float:
    """EUR/MWh réellement payé par MWh consommé par l'électrolyseur (l'énergie écrêtée est payée)."""
    if sim["used_mwh"] <= 0:
        return float("inf")
    return (sim["pv_mwh"] * pv_lcoe + sim["wind_mwh"] * wind_lcoe) / sim["used_mwh"]


def monthly_summary(sim: Dict) -> List[Dict]:
    m = month_index()[: len(sim["used_series"])]
    out = []
    for k in range(1, 13):
        sel = m == k
        out.append({"mois": k, "supply_mwh": float(sim["supply_series"][sel].sum()),
                    "used_mwh": float(sim["used_series"][sel].sum()),
                    "curtailed_mwh": float(sim["curtailed_series"][sel].sum())})
    return out


def sweep_re_ratio(base: SimConfig, pv_cf, wind_cf, ratios=(0.8, 1.0, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0),
                   pv_lcoe: float = 22.0, wind_lcoe: float = 30.0) -> List[Dict]:
    """Fait varier la capacité ENR / électrolyseur (en conservant le mix PV/éolien)."""
    mix_total = base.pv_mw + base.wind_mw
    pv_share = base.pv_mw / mix_total if mix_total else 0.5
    rows = []
    for r in ratios:
        cap = r * base.electrolyser_mw
        cfg = SimConfig(pv_mw=cap * pv_share, wind_mw=cap * (1 - pv_share),
                        electrolyser_mw=base.electrolyser_mw, min_load=base.min_load,
                        battery_mwh=base.battery_mwh, battery_mw=base.battery_mw,
                        battery_eff=base.battery_eff)
        s = simulate(cfg, pv_cf, wind_cf)
        rows.append({"ratio_ENR_electrolyseur": r, "flh": s["flh"],
                     "curtailment_pct": s["curtailment_pct"],
                     "prix_effectif_eur_mwh": effective_electricity_price(s, pv_lcoe, wind_lcoe)})
    return rows


def cost_with_simulation(sim: Dict, product: str, params, pv_lcoe: float = 22.0, wind_lcoe: float = 30.0):
    """Coût de production d'un e-fuel avec FLH et prix d'électricité issus de la simulation."""
    from dataclasses import replace
    from .efuel_economics import product_cost
    p = replace(params, flh=max(sim["flh"], 1.0),
                elec_price_eur_mwh=effective_electricity_price(sim, pv_lcoe, wind_lcoe))
    return product_cost(p, product)
