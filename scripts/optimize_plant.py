import sys
import os
import yaml
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def charger_params():
    with open("config/params.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_multicriteria_optimization():
    print("--- Système d'Aide à la Décision : Analyse Multicritère ---")
    config = charger_params()
    df_tech = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    demande_cible_t = config["demand"]["annual_h2_t"]
    crf = (config["finance"]["discount_rate"] * (1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"]) / \
          ((1 + config["finance"]["discount_rate"])**config["finance"]["lifetime_years"] - 1)
          
    # Plages de recherche élargies
    pv_options = [100, 150, 200, 250]
    wind_options = [80, 120, 160, 200]
    ely_options = [60, 70, 80, 90]
    
    resultats = []
    
    # Profils horaires (8760h)
    heures = np.arange(8760)
    solaire_cf = np.maximum(0, np.sin(2 * np.pi * (heures - 6) / 24)) * 0.85
    np.random.seed(42)
    eolien_cf = np.clip(0.4 + np.sin(2 * np.pi * heures / (24 * 7)) * 0.15 + np.random.normal(0, 0.2, 8760), 0.05, 0.95)
    
    for pv in pv_options:
        for wind in wind_options:
            for ely in ely_options:
                prod_totale = solaire_cf * pv + eolien_cf * wind
                
                # Simulation horaire simple pour évaluer la production et les pertes
                appel_max = ely
                h2_prod_total = 0
                
                for p in prod_totale:
                    util = min(p, appel_max)
                    h2_prod_total += util * 1000.0 / 52.0  # en kg
                
                h2_t = h2_prod_total / 1000.0
                taux_couv = (h2_t / demande_cible_t) * 100
                
                # Calcul CAPEX
                c_pv = df_tech.loc[df_tech['technologie'] == 'PV_Solaire', 'capex_unitaire'].values[0] * 1e3 * pv
                c_wind = df_tech.loc[df_tech['technologie'] == 'Eolien_Terrestre', 'capex_unitaire'].values[0] * 1e3 * wind
                c_ely = df_tech.loc[df_tech['technologie'] == 'Electrolyseur_PEM', 'capex_unitaire'].values[0] * 1e3 * ely
                capex_tot = c_pv + c_wind + c_ely
                
                # LCOH (€/kg)
                lcoh = (capex_tot * crf + capex_tot * 0.03) / h2_prod_total if h2_prod_total > 0 else 999
                
                # Indicateurs environnementaux et de faisabilité
                efficience_enr = 100.0 * (sum(np.minimum(prod_totale, appel_max)) / sum(prod_totale))
                ecart_cible = abs(taux_couv - 100.0)
                
                resultats.append({
                    'PV': pv, 'Wind': wind, 'Ely': ely,
                    'H2_t': h2_t, 'Couverture_%': taux_couv,
                    'LCOH': lcoh, 'CAPEX_M€': capex_tot / 1e6,
                    'Efficience_%': efficience_enr,
                    'Ecart_Cible': ecart_cible
                })

    df_res = pd.DataFrame(resultats)
    df_valides = df_res[df_res['Couverture_%'] >= 95.0].copy()
    if df_valides.empty:
        df_valides = df_res

    # 1. Meilleur niveau ÉCONOMIQUE
    best_eco = df_valides.loc[df_valides['LCOH'].idxmin()]
    # 2. Meilleur niveau ENVIRONNEMENTAL
    best_env = df_valides.loc[df_valides['Efficience_%'].idxmax()]
    # 3. Meilleur niveau TECHNIQUE
    best_tech = df_valides.loc[df_valides['Ecart_Cible'].idxmin()]
    # 4. Meilleur niveau FAISABILITÉ & COMPROMIS GLOBAL
    df_valides['Score_Global'] = df_valides['LCOH'] * (1 + df_valides['Ecart_Cible'] / 100)
    best_feas = df_valides.loc[df_valides['Score_Global'].idxmin()]

    print("\n" + "="*60)
    print("🏆 RÉSULTATS DE L'ANALYSE MULTICRITÈRE (SYSTÈME D'AIDE À LA DÉCISION)")
    print("="*60)
    
    print(f"\n1. 💰 PILIER ÉCONOMIQUE (Minimisation du LCOH) :")
    print(f"   Config : {best_eco['PV']} MW PV | {best_eco['Wind']} MW Éolien | {best_eco['Ely']} MW Électrolyseur")
    print(f"   LCOH : {best_eco['LCOH']:.2f} €/kg | CAPEX : {best_eco['CAPEX_M€']:.1f} M€ | H2 : {best_eco['H2_t']:,.0f} t/an")

    print(f"\n2. 🌿 PILIER ENVIRONNEMENTAL (Efficience maximale de la ressource) :")
    print(f"   Config : {best_env['PV']} MW PV | {best_env['Wind']} MW Éolien | {best_env['Ely']} MW Électrolyseur")
    print(f"   Efficience EnR : {best_env['Efficience_%']:.1f}% | LCOH : {best_env['LCOH']:.2f} €/kg")

    print(f"\n3. ⚡ PILIER TECHNIQUE (Adéquation parfaite avec la cible 10 000 t) :")
    print(f"   Config : {best_tech['PV']} MW PV | {best_tech['Wind']} MW Éolien | {best_tech['Ely']} MW Électrolyseur")
    print(f"   Production : {best_tech['H2_t']:,.0f} t/an (Couverture : {best_tech['Couverture_%']:.1f}%) | LCOH : {best_tech['LCOH']:.2f} €/kg")

    print(f"\n4. ⚖️ PILIER FAISABILITÉ & COMPROMIS GLOBAL (Équilibre Coût/Technique) :")
    print(f"   Config : {best_feas['PV']} MW PV | {best_feas['Wind']} MW Éolien | {best_feas['Ely']} MW Électrolyseur")
    print(f"   LCOH : {best_feas['LCOH']:.2f} €/kg | Production : {best_feas['H2_t']:,.0f} t/an | CAPEX : {best_feas['CAPEX_M€']:.1f} M€")
    print("="*60)

if __name__ == "__main__":
    run_multicriteria_optimization()