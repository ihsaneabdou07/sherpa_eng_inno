import sys
import os

# Ajouter la racine du projet au chemin de recherche Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from economics.lcoe import annualized_cost, lcoe
from models.electrolyzer import hydrogen_kg_per_h

def simulation_electrolyseur():
    # 1. Charger la base unifiée
    df = pd.read_csv("data/processed/base_techno_unifiee.csv")
    
    # 2. Extraire les paramètres de l'électrolyseur PEM
    pem_row = df[df['technologie'] == 'Electrolyseur_PEM'].iloc[0]
    
    capex_kw = pem_row['capex_unitaire']  # ex: 800 €/kW
    opex_pct = pem_row['opex_pourcent'] / 100.0  # ex: 3.5% -> 0.035
    duree_vie = int(pem_row['duree_vie_ans'])  # ex: 15 ans
    taux_actualisation = 0.07  # taux d'actualisation de 7%
    
    # 3. Calculer les coûts annualisés pour une capacité nominale de 1000 kW (1 MW)
    p_nom = 1000.0
    capex_total = capex_kw * p_nom
    
    cout_annuel = annualized_cost(capex_total, opex_pct, taux_actualisation, duree_vie)
    print(f"Coût annualisé pour 1 MW d'électrolyseur PEM : {cout_annuel:,.2f} €/an")

if __name__ == "__main__":
    simulation_electrolyseur()