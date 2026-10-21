import sys
import os
import yaml
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def charger_params():
    with open("config/params.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_efuels_optimization():
    print("--- Système d'Aide à la Décision : Intégration E-Fuels (E-Méthanol) ---")
    config = charger_params()
    df_tech = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    demande_cible_t = config["demand"]["annual_h2_t"]
    crf = (config["finance"]["discount_rate"] * (1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"]) / \
          ((1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"] - 1)
          
    # Paramètres de l'eau et de l'E-méthanol
    ratio_eau_l_kg = 9.0
    conso_electrique_eau = 3.5  # kWh/m3
    capex_eau_unitaire_jour = 14000.0 / 11.0
    opex_eau_m3 = 5.0 / 11.0
    
    # Paramètres E-Méthanol & CO2
    # 1 t H2 produit ~ 5.29 t e-méthanol
    # Coût de capture du CO2 : ~150 €/t CO2 (incluant CAPEX/OPEX capture DAC)
    cout_co2_tonne = 150.0 
    masse_co2_par_t_methanol = 1.374
    masse_h2_par_t_methanol = 0.189
    capex_synthese_unitaire_kw = 450.0  # CAPEX unitaire de l'unité de synthèse (exprimé par kW équivalent méthanol)
    
    # Plages de recherche
    pv_options = [100, 150, 200]
    wind_options = [80, 120, 160]
    ely_options = [70, 80, 90]
    
    resultats = []
    
    heures = np.arange(8760)
    solaire_cf = np.maximum(0, np.sin(2 * np.pi * (heures - 6) / 24)) * 0.85
    np.random.seed(42)
    eolien_cf = np.clip(0.4 + np.sin(2 * np.pi * heures / (24 * 7)) * 0.15 + np.random.normal(0, 0.2, 8760), 0.05, 0.95)
    
    for pv in pv_options:
        for wind in wind_options:
            for ely in ely_options:
                prod_totale = solaire_cf * pv + eolien_cf * wind
                
                appel_max = ely
                h2_prod_total_kg = 0
                
                for p in prod_totale:
                    util = min(p, appel_max)
                    h2_prod_total_kg += util * 1000.0 / 52.0
                
                h2_t = h2_prod_total_kg / 1000.0
                taux_couv = (h2_t / demande_cible_t) * 100
                
                # Eau
                volume_eau_m3_an = (h2_prod_total_kg * ratio_eau_l_kg) / 1000.0
                debit_journalier_m3_j = volume_eau_m3_an / 365.0
                
                # Énergie EnR
                c_pv = df_tech.loc[df_tech['technologie'] == 'PV_Solaire', 'capex_unitaire'].values[0] * 1e3 * pv
                c_wind = df_tech.loc[df_tech['technologie'] == 'Eolien_Terrestre', 'capex_unitaire'].values[0] * 1e3 * wind
                c_ely = df_tech.loc[df_tech['technologie'] == 'Electrolyseur_PEM', 'capex_unitaire'].values[0] * 1e3 * ely
                
                # Eau CAPEX/OPEX
                capex_eau = debit_journalier_m3_j * capex_eau_unitaire_jour
                opex_eau_annuel = volume_eau_m3_an * opex_eau_m3
                
                # E-Méthanol & CO2
                methanol_t_an = h2_t * (1.0 / masse_h2_par_t_methanol)
                co2_requis_t_an = methanol_t_an * masse_co2_par_t_methanol
                cout_annuel_co2 = co2_requis_t_an * cout_co2_tonne
                
                # CAPEX Unité de synthèse (estimé sur la base de la capacité annuelle)
                capex_synthese = (methanol_t_an * 1000.0 / 8000.0) * capex_synthese_unitaire_kw # 8000h équivalentes
                
                capex_tot_global = c_pv + c_wind + c_ely + capex_eau + capex_synthese
                opex_tot_annuel = (capex_tot_global * 0.03) + opex_eau_annuel + cout_annuel_co2
                
                # Coût annualisé et LCOH / LCOM (Levelized Cost of Methanol)
                cout_total_annuel = (capex_tot_global * crf) + opex_tot_annuel
                lcoh = cout_total_annuel / h2_prod_total_kg if h2_prod_total_kg > 0 else 999
                lcom = cout_total_annuel / (methanol_t_an * 1000.0) if methanol_t_an > 0 else 999
                
                resultats.append({
                    'PV': pv, 'Wind': wind, 'Ely': ely,
                    'H2_t': h2_t, 'Methanol_t': methanol_t_an,
                    'CO2_t': co2_requis_t_an,
                    'LCOH': lcoh, 'LCOM': lcom,
                    'CAPEX_M€': capex_tot_global / 1e6
                })

    df_res = pd.DataFrame(resultats)
    best_efuel = df_res.loc[df_res['LCOM'].idxmin()]

    print("\n" + "="*65)
    print("🏆 RÉSULTATS DE LA SYNTHÈSE E-FUELS (E-MÉTHANOL)")
    print("="*65)
    print(f"   Config optimale : {best_efuel['PV']} MW PV | {best_efuel['Wind']} MW Éolien | {best_efuel['Ely']} MW Électrolyseur")
    print(f"   Hydrogène produit : {best_efuel['H2_t']:,.0f} t/an")
    print(f"   CO2 capturé requis : {best_efuel['CO2_t']:,.0f} t/an")
    print(f"   E-Méthanol produit : {best_efuel['Methanol_t']:,.0f} t/an")
    print(f"   LCOH global : {best_efuel['LCOH']:.2f} €/kg H2")
    print(f"   Coût de l'E-Méthanol (LCOM) : {best_efuel['LCOM']:.2f} €/kg (€/t : {best_efuel['LCOM']*1000:,.0f} €/t)")
    print(f"   CAPEX Global Complexe : {best_efuel['CAPEX_M€']:.1f} M€")
    print("="*65)

if __name__ == "__main__":
    run_efuels_optimization()