import sys
import os
import yaml
import pandas as pd
import numpy as np

# Ajouter la racine du projet au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def charger_configuration():
    """Charge le fichier de configuration YAML."""
    with open("config/params.yaml", "r", encoding="utf-8") as f:
        params = yaml.safe_load(f)
    return params

def generer_profils_horaires_laayoune():
    """Génère les facteurs de charge horaires (8760h) pour le solaire et l'éolien."""
    heures = np.arange(8760)
    
    # Profil Solaire (cycle jour/nuit)
    solaire_cf = np.maximum(0, np.sin(2 * np.pi * (heures - 6) / 24)) * 0.85
    solaire_cf = solaire_cf * (1 + 0.15 * np.cos(2 * np.pi * heures / 8760))
    solaire_cf[solaire_cf < 0.02] = 0.0
    
    # Profil Éolien
    np.random.seed(42)
    bruit = np.random.normal(0, 0.2, 8760)
    eolien_cf = 0.4 + np.sin(2 * np.pi * heures / (24 * 7)) * 0.15 + bruit
    eolien_cf = np.clip(eolien_cf, 0.05, 0.95)
    
    df_profils = pd.DataFrame({
        'heure': heures,
        'pv_cf': solaire_cf,
        'wind_cf': eolien_cf
    })
    return df_profils

def calculer_crf(taux_actualisation, duree_vie):
    """Calcule le Capital Recovery Factor (Facteur de recouvrement du capital)."""
    return (taux_actualisation * (1 + taux_actualisation)**duree_vie) / ((1 + taux_actualisation)**duree_vie - 1)

def main():
    print("--- Étape 4.5 : Simulation techno-économique & Calcul du LCOH ---")
    
    # 1. Chargement des configs et données
    config = charger_configuration()
    df_tech = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    demande_cible_t = config["demand"]["annual_h2_t"]
    taux_act = config["finance"]["discount_rate"]
    duree_vie = config["finance"]["lifetime_years"]
    crf = calculer_crf(taux_act, duree_vie)
    
    # 2. Paramètres de dimensionnement (ajustés pour tendre vers 10 000 t)
    pv_mw = 200.0
    wind_mw = 120.0
    electrolyseur_mw = 70.0
    batterie_mwh = 200.0
    
    # 3. Simulation horaire
    df_profils = generer_profils_horaires_laayoune()
    prod_pv = df_profils['pv_cf'] * pv_mw
    prod_wind = df_profils['wind_cf'] * wind_mw
    prod_totale = prod_pv + prod_wind
    
    conso_specifique = 52.0  # kWh / kg H2
    soc_batterie = 0.0
    h2_produit_total_kg = 0.0
    
    for p_enr in prod_totale:
        energie_dispo = p_enr
        appel_electrolyseur_max = electrolyseur_mw * 1.0
        
        if energie_dispo >= appel_electrolyseur_max:
            energie_utilisee = appel_electrolyseur_max
            surplus = energie_dispo - appel_electrolyseur_max
            soc_batterie = min(batterie_mwh, soc_batterie + surplus)
        else:
            deficit = appel_electrolyseur_max - energie_dispo
            if soc_batterie >= deficit:
                soc_batterie -= deficit
                energie_utilisee = appel_electrolyseur_max
            else:
                energie_utilisee = energie_dispo + soc_batterie
                soc_batterie = 0.0
                
        h2_heure_kg = (energie_utilisee * 1000.0) / conso_specifique
        h2_produit_total_kg += h2_heure_kg
        
    h2_produit_t = h2_produit_total_kg / 1000.0
    
    # 4. Évaluation Économique (LCOH corrigée)
    # capex_unitaire est en €/kW, donc on multiplie par 1e3 (kW/MW) et par la puissance en MW
    capex_pv = (
        df_tech.loc[df_tech['technologie'] == 'PV_Solaire', 'capex_unitaire'].values[0]
        * 1e3
        * pv_mw
    )
    capex_wind = (
        df_tech.loc[
            df_tech['technologie'] == 'Eolien_Terrestre', 'capex_unitaire'
        ].values[0]
        * 1e3
        * wind_mw
    )
    capex_batt = (
        df_tech.loc[
            df_tech['technologie'] == 'Batterie_Li-Ion', 'capex_unitaire'
        ].values[0]
        * 1e3
        * batterie_mwh
    )
    capex_ely = (
        df_tech.loc[
            df_tech['technologie'] == 'Electrolyseur_PEM', 'capex_unitaire'
        ].values[0]
        * 1e3
        * electrolyseur_mw
    )

    capex_total = capex_pv + capex_wind + capex_batt + capex_ely

    # Annuités de capital (CAPEX annualisé)
    capex_annualise = capex_total * crf

    # OPEX estimé (3% du CAPEX total par an)
    opex_annuel = capex_total * 0.03

    # Coût total annualisé et LCOH
    cout_total_annuel = capex_annualise + opex_annuel
    lcoh = (
        cout_total_annuel / h2_produit_total_kg
    )  # € / kg H2 (car h2_produit_total_kg est en kg)
    
    print(f"\n--- Résultats du Dimensionnement Ajusté ---")
    print(f"Puissance PV : {pv_mw} MW | Éolien : {wind_mw} MW | Électrolyseur : {electrolyseur_mw} MW")
    print(f"H2 Produit : {h2_produit_t:,.2f} tonnes/an (Cible : {demande_cible_t} t)")
    print(f"CAPEX Total : {capex_total / 1e6:.2f} M€")
    print(f"Coût de l'hydrogène (LCOH) : {lcoh:.2f} €/kg H2")

if __name__ == "__main__":
    main()