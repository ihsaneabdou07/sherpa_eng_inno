"""
app/efuels_page.py — Page Streamlit « E-fuels » du prototype Sherpa Engineering.

Lancer seule :        streamlit run app/efuels_page.py
Dans une app multipage : copier ce fichier dans app/pages/ (ex. app/pages/3_E_fuels.py)
                         ou l'importer et appeler render().

Lit les modules economics/efuel_economics.py et economics/hourly_sim.py.
Profils PV/éolien : SYNTHÉTIQUES par défaut (démo) ; importer un CSV réel (pv_cf, wind_cf, 8760 lignes).
Source des paramètres de coût : Colelli et al. (2026) [ART] + hypothèses Sherpa [HYP] (voir HYPOTHESES_EFUEL.md).
"""
from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if ROOT.name == "pages":                      # copie dans app/pages/
    ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from economics.efuel_economics import Params, PRODUCTS, lcoh, product_cost, plant_sizing   # noqa: E402
from economics.hourly_sim import (SimConfig, synthetic_profiles, load_profiles_csv, simulate,   # noqa: E402
                                  monthly_summary, effective_electricity_price, cost_with_simulation)

MONTHS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
PRODUCT_LABELS = {"e-methanol": "e-méthanol", "e-DME": "e-DME", "e-kerosene": "e-kérosène",
                  "e-diesel": "e-diesel", "e-gasoline": "e-essence", "e-ammonia": "e-ammoniac"}


@st.cache_data(show_spinner=False)
def _synthetic(pv_cf: float, wind_cf: float, latitude: float, seed: int):
    return synthetic_profiles(pv_cf, wind_cf, latitude, seed)


def _load_uploaded(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(file.getvalue())
        path = tmp.name
    try:
        return load_profiles_csv(path)
    finally:
        os.unlink(path)


def render() -> None:
    st.title("E-fuels liquides — simulation et coûts (Maroc)")
    st.caption("Pré-faisabilité (±30–50 %). Paramètres [ART] = Colelli et al. 2026 ; [HYP] = hypothèses Sherpa à valider. "
               "Les profils ENR par défaut sont synthétiques (démo).")

    # ------------------------------------------------------------------ entrées
    with st.sidebar:
        st.header("Électrolyse et finance")
        tech = st.selectbox("Technologie d'électrolyse", ["PEM", "AEL", "SOEC"], index=0)
        co2_label = st.selectbox("Source de CO2", ["Point source (industrie, biogénique)", "DAC (capture dans l'air)"], index=0)
        co2_type = "dac" if co2_label.startswith("DAC") else "point_source"
        wacc = st.slider("WACC (%)", min_value=4.0, max_value=15.0, value=8.0, step=0.5) / 100.0
        life = st.slider("Durée de vie (ans)", min_value=10, max_value=30, value=20, step=1)
        st.header("Parc ENR et électrolyseur")
        pv_mw = st.number_input("PV (MW)", min_value=0.0, value=300.0, step=10.0)
        wind_mw = st.number_input("Éolien (MW)", min_value=0.0, value=200.0, step=10.0)
        el_mw = st.number_input("Électrolyseur (MW)", min_value=1.0, value=250.0, step=10.0)
        min_load = st.slider("Charge minimale électrolyseur (%)", min_value=0, max_value=40, value=10, step=5) / 100.0
        batt_mwh = st.number_input("Batterie — énergie (MWh)", min_value=0.0, value=0.0, step=50.0)
        batt_mw = st.number_input("Batterie — puissance (MW)", min_value=0.0, value=0.0, step=10.0)
        pv_lcoe = st.number_input("Coût PV (€/MWh) [HYP]", min_value=5.0, value=22.0, step=1.0)
        wind_lcoe = st.number_input("Coût éolien (€/MWh) [HYP]", min_value=5.0, value=30.0, step=1.0)
        st.header("Profils horaires")
        mode = st.radio("Source des profils", ["Synthétiques (démo)", "Importer un CSV (pv_cf, wind_cf)"], index=0)
        pv_cf = wind_cf = None
        if mode.startswith("Importer"):
            up = st.file_uploader("CSV 8760 lignes (colonnes pv_cf, wind_cf entre 0 et 1)", type=["csv"])
            if up is not None:
                try:
                    pv_cf, wind_cf = _load_uploaded(up)
                except Exception as exc:                       # noqa: BLE001
                    st.error(f"CSV invalide : {exc}")
        if pv_cf is None:
            t_pv = st.slider("Facteur de charge PV cible", min_value=0.15, max_value=0.40, value=0.30, step=0.01)
            t_wd = st.slider("Facteur de charge éolien cible", min_value=0.20, max_value=0.60, value=0.45, step=0.01)
            lat = st.slider("Latitude (°N)", min_value=20.0, max_value=36.0, value=28.0, step=0.5)
            seed = st.number_input("Graine aléatoire", min_value=1, value=1, step=1)
            pv_cf, wind_cf = _synthetic(t_pv, t_wd, lat, int(seed))
        st.header("Usine cible")
        tonnes = st.number_input("Production annuelle (t/an)", min_value=1000.0, value=100000.0, step=10000.0)
        focus = st.selectbox("Produit en focus", list(PRODUCTS), index=0, format_func=lambda k: PRODUCT_LABELS[k])

    base = Params(tech=tech, co2_type=co2_type, wacc=wacc, life_years=float(life))
    cfg = SimConfig(pv_mw=pv_mw, wind_mw=wind_mw, electrolyser_mw=el_mw, min_load=min_load,
                    battery_mwh=batt_mwh, battery_mw=batt_mw)
    sim = simulate(cfg, pv_cf, wind_cf)
    eff_price = effective_electricity_price(sim, pv_lcoe, wind_lcoe)
    kwh_kg = lcoh(base)["kwh_per_kg"]
    h2_t = sim["used_mwh"] * 1000.0 / kwh_kg / 1000.0
    ratio = (pv_mw + wind_mw) / el_mw

    default_p = replace(base, elec_price_eur_mwh=30.0, flh=5000.0)
    sim_p = replace(base, elec_price_eur_mwh=eff_price, flh=max(sim["flh"], 1.0))

    tabs = st.tabs(["Simulation horaire", "Coûts par e-fuel", "Dimensionnement ENR", "Usine cible", "Hypothèses et limites"])

    # ------------------------------------------------------------------ 1. simulation
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Heures pleine charge", f"{sim['flh']:,.0f} h/an")
        c2.metric("Énergie écrêtée", f"{sim['curtailment_pct']:.1%}")
        c3.metric("Prix effectif électricité", f"{eff_price:,.1f} €/MWh")
        c4.metric("Hydrogène", f"{h2_t:,.0f} t/an")
        st.write(f"Rapport ENR / électrolyseur : **{ratio:.2f}** · Heures de fonctionnement : **{sim['hours_running']:,}** · "
                 f"Démarrages : **{sim['starts']}** · Facteur de charge ENR : **{sim['re_capacity_factor']:.1%}**")
        if sim["flh"] < 3000:
            st.warning("Moins de 3 000 h/an : l'électrolyseur est sous-utilisé (le CAPEX pèse fortement sur le coût de l'hydrogène).")
        week = st.slider("Semaine affichée (jour de départ)", min_value=1, max_value=358, value=180, step=1)
        a, b = (week - 1) * 24, (week - 1) * 24 + 7 * 24
        df_w = pd.DataFrame({"Production ENR (MW)": sim["supply_series"][a:b],
                             "Électrolyseur (MW)": sim["used_series"][a:b],
                             "Écrêté (MW)": sim["curtailed_series"][a:b]})
        st.subheader("Semaine type")
        st.line_chart(df_w)
        ms = pd.DataFrame(monthly_summary(sim))
        ms["Mois"] = MONTHS
        ms["FLH du mois (h)"] = ms["used_mwh"] / el_mw
        st.subheader("Synthèse mensuelle")
        st.bar_chart(ms.set_index("Mois")[["FLH du mois (h)"]])
        st.dataframe(ms[["Mois", "supply_mwh", "used_mwh", "curtailed_mwh", "FLH du mois (h)"]]
                     .rename(columns={"supply_mwh": "Production (MWh)", "used_mwh": "Électrolyseur (MWh)",
                                      "curtailed_mwh": "Écrêté (MWh)"}).round(0))

    # ------------------------------------------------------------------ 2. coûts
    with tabs[1]:
        st.subheader("Coût de production : hypothèse par défaut vs simulation")
        rows = []
        for k in PRODUCTS:
            d, s = product_cost(default_p, k), product_cost(sim_p, k)
            rows.append({"Produit": PRODUCT_LABELS[k], "Défaut 30 €/MWh, 5 000 h (€/t)": d["total_eur_t"],
                         "Simulation (€/t)": s["total_eur_t"], "Simulation (€/MWh PCI)": s["total_eur_mwh"],
                         "Efficacité élec.→carburant": s["efficiency"], "Eau (m³/t)": s["water_m3_per_t"],
                         "Part H2": s["h2_share"]})
        df = pd.DataFrame(rows)
        st.bar_chart(df.set_index("Produit")[["Défaut 30 €/MWh, 5 000 h (€/t)", "Simulation (€/t)"]])
        st.dataframe(df.round(2))
        lc_d, lc_s = lcoh(default_p)["total"], lcoh(sim_p)["total"]
        st.write(f"LCOH : **{lc_s:.2f} €/kg** avec la simulation contre **{lc_d:.2f} €/kg** avec l'hypothèse par défaut "
                 f"(article : 3–6 €/kg).")
        comp = product_cost(sim_p, focus)
        st.subheader(f"Décomposition — {PRODUCT_LABELS[focus]} (simulation)")
        st.bar_chart(pd.DataFrame({"€/t": [comp["cost_h2"], comp["cost_co2"], comp["cost_synth_capex"], comp["cost_synth_elec"]]},
                                  index=["Hydrogène", "CO2", "CAPEX synthèse", "Électricité synthèse/N2"]))

    # ------------------------------------------------------------------ 3. sizing
    with tabs[2]:
        st.subheader("Surdimensionnement ENR : heures gagnées vs prix de l'énergie écrêtée")
        mix = pv_mw + wind_mw
        share = pv_mw / mix if mix else 0.5
        ratios = [0.8, 1.0, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0]
        out = []
        for r in ratios:
            cap = r * el_mw
            c = SimConfig(pv_mw=cap * share, wind_mw=cap * (1 - share), electrolyser_mw=el_mw, min_load=min_load,
                          battery_mwh=batt_mwh, battery_mw=batt_mw)
            s = simulate(c, pv_cf, wind_cf)
            cost = cost_with_simulation(s, focus, base, pv_lcoe, wind_lcoe)["total_eur_t"]
            out.append({"Rapport ENR/électrolyseur": r, "FLH (h/an)": s["flh"], "Écrêtage": s["curtailment_pct"],
                        "Prix effectif (€/MWh)": effective_electricity_price(s, pv_lcoe, wind_lcoe),
                        f"Coût {PRODUCT_LABELS[focus]} (€/t)": cost})
        sw = pd.DataFrame(out)
        cost_col = f"Coût {PRODUCT_LABELS[focus]} (€/t)"
        best = sw.loc[sw[cost_col].idxmin()]
        st.success(f"Coût minimal pour {PRODUCT_LABELS[focus]} : rapport ENR/électrolyseur ≈ **{best['Rapport ENR/électrolyseur']:.1f}** "
                   f"→ {best['FLH (h/an)']:,.0f} h/an, {best[cost_col]:,.0f} €/t (profils {'importés' if mode.startswith('Importer') and pv_cf is not None else 'synthétiques'}).")
        st.line_chart(sw.set_index("Rapport ENR/électrolyseur")[["FLH (h/an)"]])
        st.line_chart(sw.set_index("Rapport ENR/électrolyseur")[[cost_col]])
        st.dataframe(sw.round(3))

    # ------------------------------------------------------------------ 4. usine
    with tabs[3]:
        st.subheader(f"Usine de {tonnes:,.0f} t/an — dimensionnement avec les FLH simulées")
        rows = []
        for k in PRODUCTS:
            z = plant_sizing(sim_p, k, tonnes)
            rows.append({"Produit": PRODUCT_LABELS[k], "H2 (t/an)": z["h2_t_per_year"], "CO2 (t/an)": z["co2_t_per_year"],
                         "N2 (t/an)": z["n2_t_per_year"], "Électrolyseur (MW)": z["electrolyser_mw"],
                         "ENR équivalente (MW)": z["electrolyser_mw"] * ratio,
                         "Électricité électrolyse (GWh/an)": z["electricity_gwh_per_year"],
                         "Eau dessalée (m³/jour)": z["water_m3_per_year"] / 365.0})
        st.dataframe(pd.DataFrame(rows).round(1))
        st.info("ENR équivalente = puissance d'électrolyseur × rapport ENR/électrolyseur choisi. Le CAPEX détaillé est dans "
                "capex_data.xlsx (feuille Dimensionnement) ; cette page ne chiffre pas le CAPEX.")

    # ------------------------------------------------------------------ 5. limites
    with tabs[4]:
        st.markdown("""
**Ce que fait le modèle** : simulation horaire (électrolyseur = min(production ENR ; puissance nominale), arrêt sous la charge minimale,
batterie optionnelle), prix effectif de l'électricité (l'énergie écrêtée est payée), coût de production des 6 e-fuels.

**Limites**
- Profils **synthétiques** par défaut : ils ne représentent pas un site réel. Importer des séries mesurées/modélisées pour toute décision.
- Pas de rampes, dégradation, disponibilité, pertes réseau, stockage H2, ni charge de synthèse/captage dans la simulation.
- Les coûts de l'article proviennent de sources hétérogènes ; le prix de l'électricité et les heures de charge dominent le résultat.
- Valeurs `[HYP]` (CAPEX FT, coûts ENR, WACC, facteur Maroc) à valider avec des devis et des données du site.

**Sources** : Colelli et al. (2026), *Energy Conversion and Management*, doi:10.1016/j.enconman.2025.120529.
""")


if __name__ == "__main__":
    st.set_page_config(page_title="E-fuels — Sherpa Engineering", layout="wide")
    render()
