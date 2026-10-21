import sys
import os
import yaml
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def charger_params():
    with open("config/params.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_multicriteria_optimization_with_water():
    print("--- Système d'Aide à la Décision : Intégration Énergie & Eau (Laâyoune) ---")
    config = charger_params()
    df_tech = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    demande_cible_t = config["demand"]["annual_h2_t"]
    crf = (config["finance"]["discount_rate"] * (1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"]) / \
          ((1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"] - 1)
          
    # Paramètres de l'eau (basés sur votre base Excel de Laâyoune)
    ratio_eau_l_kg = 9.0  # litres d'eau par kg d'H2
    conso_electrique_eau = 3.5  # kWh / m3 (Osmose inverse + prise d'eau)
    capex_eau_unitaire_jour = 14000.0 / 11.0  # ~1270 €/(m3/jour)
    opex_eau_m3 = 5.0 / 11.0  # ~0.45 €/m3
    
    # Plages de recherche
    pv_options = [100, 150, 200, 250]
    wind_options = [80, 120, 160, 200]
    ely_options = [60, 70, 80, 90]
    
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
                    h2_prod_total_kg += util * 1000.0 / 52.0  # en kg
                
                h2_t = h2_prod_total_kg / 1000.0
                taux_couv = (h2_t / demande_cible_t) * 100
                
                # Calcul des besoins en eau
                volume_eau_m3_an = (h2_prod_total_kg * ratio_eau_l_kg) / 1000.0
                debit_journalier_m3_j = volume_eau_m3_an / 365.0
                
                # CAPEX et OPEX du système énergétique
                c_pv = df_tech.loc[df_tech['technologie'] == 'PV_Solaire', 'capex_unitaire'].values[0] * 1e3 * pv
                c_wind = df_tech.loc[df_tech['technologie'] == 'Eolien_Terrestre', 'capex_unitaire'].values[0] * 1e3 * wind
                c_ely = df_tech.loc[df_tech['technologie'] == 'Electrolyseur_PEM', 'capex_unitaire'].values[0] * 1e3 * ely
                
                # CAPEX et OPEX du Bloc Eau
                capex_eau = debit_journalier_m3_j * capex_eau_unitaire_jour
                opex_eau_annuel = volume_eau_m3_an * opex_eau_m3
                
                capex_tot_global = c_pv + c_wind + c_ely + capex_eau
                opex_tot_annuel = (capex_tot_global * 0.03) + opex_eau_annuel
                
                # LCOH global incluant l'eau (€/kg)
                cout_total_annuel = (capex_tot_global * crf) + opex_tot_annuel
                lcoh = cout_total_annuel / h2_prod_total_kg if h2_prod_total_kg > 0 else 999
                
                efficience_enr = 100.0 * (sum(np.minimum(prod_totale, appel_max)) / sum(prod_totale))
                ecart_cible = abs(taux_couv - 100.0)
                
                resultats.append({
                    'PV': pv, 'Wind': wind, 'Ely': ely,
                    'H2_t': h2_t, 'Couverture_%': taux_couv,
                    'LCOH': lcoh, 'CAPEX_M€': capex_tot_global / 1e6,
                    'Eau_m3_an': volume_eau_m3_an,
                    'Efficience_%': efficience_enr,
                    'Ecart_Cible': ecart_cible
                })

    df_res = pd.DataFrame(resultats)
    df_valides = df_res[df_res['Couverture_%'] >= 95.0].copy()
    if df_valides.empty:
        df_valides = df_res

    best_eco = df_valides.loc[df_valides['LCOH'].idxmin()]
    df_valides['Score_Global'] = df_valides['LCOH'] * (1 + df_valides['Ecart_Cible'] / 100)
    best_feas = df_valides.loc[df_valides['Score_Global'].idxmin()]

    print("\n" + "="*65)
    print("🏆 RÉSULTATS MULTICRITÈRES AVEC INTÉGRATION DU BLOC EAU (LAÂYOUNE)")
    print("="*65)
    print(f"\n1. 💰 MEILLEURE CONFIGURATION ÉCONOMIQUE & EAU :")
    print(f"   Config : {best_eco['PV']} MW PV | {best_eco['Wind']} MW Éolien | {best_eco['Ely']} MW Électrolyseur")
    print(f"   LCOH (avec eau) : {best_eco['LCOH']:.2f} €/kg | CAPEX Global : {best_eco['CAPEX_M€']:.1f} M€")
    print(f"   Consommation d'eau : {best_eco['Eau_m3_an']:,.0f} m³/an | H2 : {best_eco['H2_t']:,.0f} t/an")

    print(f"\n2. ⚖️ MEILLEUR COMPROMIS GLOBAL :")
    print(f"   Config : {best_feas['PV']} MW PV | {best_feas['Wind']} MW Éolien | {best_feas['Ely']} MW Électrolyseur")
    print(f"   LCOH : {best_feas['LCOH']:.2f} €/kg | Couverture : {best_feas['Couverture_%']:.1f}%")
    print("="*65)

if __name__ == "__main__":
    run_multicriteria_optimization_with_water()