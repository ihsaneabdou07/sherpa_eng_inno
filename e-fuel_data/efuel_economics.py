"""
efuel_economics.py
Module economics/ : calcul technico-économique simplifié des e-fuels liquides.

Objectif : reproduire en Python la logique du classeur
`efuels_maroc_base_donnees.xlsx` (feuille Calculateur_LCOE) afin de l'intégrer
au prototype d'aide à la décision (PV, éolien, stockage, dessalement,
électrolyse, carburants de synthèse).

Sources des paramètres :
  [ART] Colelli et al. (2026), Energy Conversion and Management,
        doi:10.1016/j.enconman.2025.120529
  [HYP] hypothèse Sherpa à valider (voir docs/HYPOTHESES_EFUEL.md)
Toutes les valeurs [HYP] doivent être confrontées à des données Maroc
(offres de prix, devis, mesures de site) avant décision d'investissement.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict

# --------------------------------------------------------------------------
# Constantes physiques (valeurs usuelles)
# --------------------------------------------------------------------------
M_H2, M_CO2, M_N2 = 2.016, 44.01, 28.014            # g/mol
M_MEOH, M_DME, M_NH3, M_CH2 = 32.04, 46.07, 17.031, 14.027
H2_DENSITY_KG_PER_NM3 = 0.08988                      # kg/Nm3 (0 °C, 1 atm)
HOURS_PER_YEAR = 8760

# --------------------------------------------------------------------------
# Électrolyseurs : [ART] Table 4 (min, max) ; SOEC capex/opex = [HYP]
# --------------------------------------------------------------------------
ELECTROLYSERS: Dict[str, Dict[str, tuple]] = {
    "AEL":  {"capex_eur_kw": (800, 1500),  "kwh_nm3": (5.0, 5.9), "opex_pct": (2.0, 3.0)},
    "PEM":  {"capex_eur_kw": (1400, 2100), "kwh_nm3": (5.0, 5.6), "opex_pct": (3.0, 5.0)},
    "SOEC": {"capex_eur_kw": (2000, 2500), "kwh_nm3": (3.7, 3.9), "opex_pct": (3.0, 5.0)},
}

# Coût de capture du CO2 en USD/t : [ART] Table 2 (méthode de référence par type)
CO2_COST_USD_T = {
    "point_source": (50, 100),   # absorption chimique
    "dac": (235, 600),           # Direct Air Capture
}
# Énergie de capture (MWh/t CO2, équivalent) : point source [HYP], DAC [ART] (chaleur 1.5-2.5 + élec 0.5-1 -> milieu)
CO2_CAPTURE_MWH_T = {"point_source": 0.25, "dac": 2.75}

# --------------------------------------------------------------------------
# Produits : PCI [std], capex conversion €/kW_fuel (proche terme) [ART] sauf FT [HYP],
# électricité de synthèse kWh/t (FT = 500 [ART] ; autres [HYP]), prix fossile [HYP]
# --------------------------------------------------------------------------
PRODUCTS: Dict[str, Dict] = {
    "e-methanol":  {"lhv": 19.9, "capex": (300, 1200),  "synth_kwh_t": 150, "fossil": (300, 450)},
    "e-DME":       {"lhv": 28.4, "capex": (300, 1200),  "synth_kwh_t": 150, "fossil": (400, 700)},
    "e-kerosene":  {"lhv": 43.1, "capex": (1000, 1800), "synth_kwh_t": 500, "fossil": (650, 900)},
    "e-diesel":    {"lhv": 43.0, "capex": (1000, 1800), "synth_kwh_t": 500, "fossil": (600, 900)},
    "e-gasoline":  {"lhv": 43.4, "capex": (600, 600),   "synth_kwh_t": 150, "fossil": (600, 900)},
    "e-ammonia":   {"lhv": 18.6, "capex": (1300, 2200), "synth_kwh_t": 150, "fossil": (350, 600)},
}


def stoichiometry(product: str) -> Dict[str, float]:
    """Intensités stœchiométriques (t de réactif par t de produit), avant rendement matière."""
    if product == "e-methanol":
        return {"h2": 3 * M_H2 / M_MEOH, "co2": M_CO2 / M_MEOH, "n2": 0.0}
    if product == "e-DME":
        return {"h2": 6 * M_H2 / M_DME, "co2": 2 * M_CO2 / M_DME, "n2": 0.0}
    if product in ("e-kerosene", "e-diesel", "e-gasoline"):   # approximation (CH2)n
        return {"h2": 3 * M_H2 / M_CH2, "co2": M_CO2 / M_CH2, "n2": 0.0}
    if product == "e-ammonia":
        return {"h2": 3 * M_H2 / (2 * M_NH3), "co2": 0.0, "n2": M_N2 / (2 * M_NH3)}
    raise KeyError(product)


@dataclass(frozen=True)
class Params:
    elec_price_eur_mwh: float = 30.0      # [HYP] ENR hybride PV+éolien, Maroc
    flh: float = 5000.0                   # [HYP] heures pleine charge électrolyseur
    tech: str = "PEM"
    co2_type: str = "point_source"
    wacc: float = 0.08                    # [HYP]
    life_years: float = 20.0              # [HYP]
    fx_eur_per_usd: float = 0.92          # [HYP]
    water_eur_m3: float = 2.0             # [HYP] eau dessalée
    water_stoich_l_kg: float = 8.92       # [ART]
    water_overuse: float = 0.25           # [ART]
    synth_utilisation: float = 0.90       # [HYP]
    synth_opex_pct: float = 0.04          # [HYP]
    material_yield: float = 0.95          # [HYP]
    n2_kwh_per_kg: float = 0.11           # [ART]


def crf(wacc: float, years: float) -> float:
    if wacc == 0:
        return 1.0 / years
    q = (1 + wacc) ** years
    return wacc * q / (q - 1)


def _mid(t) -> float:
    return (t[0] + t[1]) / 2.0


def lcoh(p: Params) -> Dict[str, float]:
    """Coût de l'hydrogène (EUR/kg) décomposé."""
    e = ELECTROLYSERS[p.tech]
    kwh_nm3 = _mid(e["kwh_nm3"])
    kwh_kg = kwh_nm3 / H2_DENSITY_KG_PER_NM3
    capex = _mid(e["capex_eur_kw"])
    opex = _mid(e["opex_pct"]) / 100.0
    elec = p.elec_price_eur_mwh * kwh_kg / 1000.0
    capex_part = capex * (crf(p.wacc, p.life_years) + opex) / (p.flh / kwh_kg)
    water_l = p.water_stoich_l_kg * (1 + p.water_overuse)
    water = p.water_eur_m3 * water_l / 1000.0
    return {"kwh_per_kg": kwh_kg, "electricity": elec, "capex_opex": capex_part,
            "water": water, "water_l_per_kg": water_l,
            "total": elec + capex_part + water}


def product_cost(p: Params, product: str) -> Dict[str, float]:
    """Coût de production (EUR/t) et indicateurs pour un e-fuel."""
    d = PRODUCTS[product]
    s = stoichiometry(product)
    h2_t = s["h2"] / p.material_yield
    co2_t = s["co2"] / p.material_yield
    n2_t = s["n2"] / p.material_yield
    h = lcoh(p)

    co2_cost_eur_t = _mid(CO2_COST_USD_T[p.co2_type]) * p.fx_eur_per_usd
    mwh_per_t_fuel = d["lhv"] * 1000.0 / 3600.0
    kw_fuel_per_tpy = mwh_per_t_fuel * 1000.0 / HOURS_PER_YEAR / p.synth_utilisation
    capex_mid = _mid(d["capex"])
    synth_capex_annuity = kw_fuel_per_tpy * capex_mid * (crf(p.wacc, p.life_years) + p.synth_opex_pct)

    synth_elec_kwh = d["synth_kwh_t"] + n2_t * 1000.0 * p.n2_kwh_per_kg
    synth_elec_cost = synth_elec_kwh / 1000.0 * p.elec_price_eur_mwh

    cost_h2 = h2_t * 1000.0 * h["total"]
    cost_co2 = co2_t * co2_cost_eur_t
    total = cost_h2 + cost_co2 + synth_capex_annuity + synth_elec_cost

    elec_mwh = (h2_t * 1000.0 * h["kwh_per_kg"] / 1000.0
                + co2_t * CO2_CAPTURE_MWH_T[p.co2_type]
                + synth_elec_kwh / 1000.0)
    return {
        "h2_t_per_t": h2_t, "co2_t_per_t": co2_t, "n2_t_per_t": n2_t,
        "cost_h2": cost_h2, "cost_co2": cost_co2,
        "cost_synth_capex": synth_capex_annuity, "cost_synth_elec": synth_elec_cost,
        "total_eur_t": total, "total_eur_mwh": total / mwh_per_t_fuel,
        "elec_mwh_per_t": elec_mwh, "efficiency": mwh_per_t_fuel / elec_mwh,
        "water_m3_per_t": h2_t * h["water_l_per_kg"],
        "h2_share": cost_h2 / total,
    }


def plant_sizing(p: Params, product: str, tonnes_per_year: float) -> Dict[str, float]:
    """Dimensionnement de base pour une production annuelle cible."""
    c = product_cost(p, product)
    h = lcoh(p)
    h2_t_yr = c["h2_t_per_t"] * tonnes_per_year
    electrolyser_mw = h2_t_yr * 1000.0 * h["kwh_per_kg"] / p.flh / 1000.0
    return {
        "h2_t_per_year": h2_t_yr,
        "co2_t_per_year": c["co2_t_per_t"] * tonnes_per_year,
        "n2_t_per_year": c["n2_t_per_t"] * tonnes_per_year,
        "electrolyser_mw": electrolyser_mw,
        "electricity_gwh_per_year": c["elec_mwh_per_t"] * tonnes_per_year / 1000.0,
        "water_m3_per_year": c["water_m3_per_t"] * tonnes_per_year,
    }


def compare_all(p: Params | None = None) -> Dict[str, Dict[str, float]]:
    p = p or Params()
    return {k: product_cost(p, k) for k in PRODUCTS}


if __name__ == "__main__":
    P = Params()
    print("LCOH:", {k: round(v, 3) for k, v in lcoh(P).items()})
    for k, v in compare_all(P).items():
        print(f"{k:12s} {v['total_eur_t']:8.0f} EUR/t  {v['total_eur_mwh']:6.0f} EUR/MWh  "
              f"eff={v['efficiency']:.2f}  H2={v['h2_share']:.0%}")
