import sys
import os
import yaml
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def charger_params():
    with open("config/params.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_full_ecosystem_optimization():
    print("--- SAD Multicritère : Écosystème Intégré (EnR + Batterie + Eau + E-Fuels) ---")
    config = charger_params()
    df_tech = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    demande_cible_t = config["demand"]["annual_h2_t"]
    crf = (config["finance"]["discount_rate"] * (1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"]) / \
          ((1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"] - 1)
          
    # Paramètres techniques et économiques
    ratio_eau_l_kg = 9.0
    conso_electrique_eau = 3.5  # kWh/m3
    capex_eau_unitaire_jour = 14000.0 / 11.0  # ~1270 €/(m3/j)
    opex_eau_m3 = 5.0 / 11.0
    
    cout_co2_tonne = 150.0 
    masse_co2_par_t_methanol = 1.374
    masse_h2_par_t_methanol = 0.189
    capex_synthese_unitaire_kw = 450.0
    
    # Paramètres Batteries (basés sur votre dossier batterie LFP)
    capex_batterie_kwh = 250.0  # €/kWh
    rendement_batterie = 0.90   # Round-trip efficiency ~90%
    
    # Plages de recherche optimisées
    pv_options = [100, 150, 200]
    wind_options = [80, 120, 160]
    ely_options = [70, 80, 90]
    batt_capacity_kwh_options = [0, 50000, 100000]  # Capacité de stockage en kWh
    
    resultats = []
    
    heures = np.arange(8760)
    solaire_cf = np.maximum(0, np.sin(2 * np.pi * (heures - 6) / 24)) * 0.85
    np.random.seed(42)
    eolien_cf = np.clip(0.4 + np.sin(2 * np.pi * heures / (24 * 7)) * 0.15 + np.random.normal(0, 0.2, 8760), 0.05, 0.95)
    
    for pv in pv_options:
        for wind in wind_options:
            for ely in ely_options:
                for batt_kwh in batt_capacity_kwh_options:
                    prod_totale = solaire_cf * pv + eolien_cf * wind
                    
                    # Simulation horaire avec gestion de la batterie
                    appel_max_ely = ely
                    h2_prod_total_kg = 0
                    soc = batt_kwh * 0.5  # Reprise à 50% de charge initiale
                    
                    for p in prod_totale:
                        energie_dispo = p
                        
                        if energie_dispo > appel_max_ely:
                            excedent = energie_dispo - appel_max_ely
                            energie_vers_batt = min(excedent, (batt_kwh - soc) / rendement_batterie)
                            soc += energie_vers_batt * rendement_batterie
                            energie_utile_ely = appel_max_ely
                        else:
                            deficit = appel_max_ely - energie_dispo
                            energie_depuis_batt = min(deficit, soc * rendement_batterie)
                            soc -= energie_depuis_batt / rendement_batterie
                            energie_utile_ely = energie_dispo + energie_depuis_batt
                            
                        h2_prod_total_kg += energie_utile_ely * 1000.0 / 52.0
                    
                    h2_t = h2_prod_total_kg / 1000.0
                    taux_couv = (h2_t / demande_cible_t) * 100
                    
                    # Eau
                    volume_eau_m3_an = (h2_prod_total_kg * ratio_eau_l_kg) / 1000.0
                    debit_journalier_m3_j = volume_eau_m3_an / 365.0
                    
                    # CAPEX EnR & Électrolyseur
                    c_pv = df_tech.loc[df_tech['technologie'] == 'PV_Solaire', 'capex_unitaire'].values[0] * 1e3 * pv
                    c_wind = df_tech.loc[df_tech['technologie'] == 'Eolien_Terrestre', 'capex_unitaire'].values[0] * 1e3 * wind
                    c_ely = df_tech.loc[df_tech['technologie'] == 'Electrolyseur_PEM', 'capex_unitaire'].values[0] * 1e3 * ely
                    
                    # CAPEX Batterie
                    capex_batt = batt_kwh * capex_batterie_kwh
                    
                    # CAPEX Eau & Synthèse E-Méthanol
                    capex_eau = debit_journalier_m3_j * capex_eau_unitaire_jour
                    opex_eau_annuel = volume_eau_m3_an * opex_eau_m3
                    
                    methanol_t_an = h2_t * (1.0 / masse_h2_par_t_methanol)
                    co2_requis_t_an = methanol_t_an * masse_co2_par_t_methanol
                    cout_annuel_co2 = co2_requis_t_an * cout_co2_tonne
                    capex_synthese = (methanol_t_an * 1000.0 / 8000.0) * capex_synthese_unitaire_kw
                    
                    capex_tot_global = c_pv + c_wind + c_ely + capex_batt + capex_eau + capex_synthese
                    opex_tot_annuel = (capex_tot_global * 0.03) + opex_eau_annuel + cout_annuel_co2
                    
                    cout_total_annuel = (capex_tot_global * crf) + opex_tot_annuel
                    lcoh = cout_total_annuel / h2_prod_total_kg if h2_prod_total_kg > 0 else 999
                    lcom = cout_total_annuel / (methanol_t_an * 1000.0) if methanol_t_an > 0 else 999
                    
                    resultats.append({
                        'PV': pv, 'Wind': wind, 'Ely': ely, 'Batt_MWh': batt_kwh / 1000.0,
                        'H2_t': h2_t, 'Methanol_t': methanol_t_an,
                        'LCOH': lcoh, 'LCOM': lcom,
                        'CAPEX_M€': capex_tot_global / 1e6
                    })

    df_res = pd.DataFrame(resultats)
    best_config = df_res.loc[df_res['LCOM'].idxmin()]

    print("\n" + "="*65)
    print("🏆 RÉSULTATS OPTIMISÉS AVEC STOCKAGE BATTERIE")
    print("="*65)
    print(f"   Config PV Solaire : {best_config['PV']} MW")
    print(f"   Config Éolien : {best_config['Wind']} MW")
    print(f"   Config Électrolyseur PEM : {best_config['Ely']} MW")
    print(f"   Capacité Batterie : {best_config['Batt_MWh']:,.1f} MWh")
    print(f"   Hydrogène produit : {best_config['H2_t']:,.0f} t/an")
    print(f"   E-Méthanol produit : {best_config['Methanol_t']:,.0f} t/an")
    print(f"   LCOH global : {best_config['LCOH']:.2f} €/kg H2")
    print(f"   Coût de l'E-Méthanol (LCOM) : {best_config['LCOM']:.2f} €/kg ({best_config['LCOM']*1000:,.0f} €/t)")
    print(f"   CAPEX Global du Complexe : {best_config['CAPEX_M€']:.1f} M€")
    print("="*65)

if __name__ == "__main__":
    run_full_ecosystem_optimization()