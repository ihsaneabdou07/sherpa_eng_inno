import pandas as pd

# Charger la base de données techno-économique unifiée
df_params = pd.read_csv("data/processed/base_techno_unifiee.csv")

# Exemple : Filtrer les paramètres pour l'électrolyseur PEM
electrolyser_params = df_params[df_params['technologie'] == 'Electrolyseur_PEM']
print(electrolyser_params)