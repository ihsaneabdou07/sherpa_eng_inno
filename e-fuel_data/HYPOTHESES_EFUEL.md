# Hypothèses — module e-fuels (à fusionner avec HYPOTHESES.md)

Légende : **[ART]** = Colelli et al. (2026), *Energy Conversion and Management*, doi:10.1016/j.enconman.2025.120529 ·
**[HYP]** = hypothèse Sherpa à valider par donnée Maroc ou devis.

| ID | Hypothèse | Valeur par défaut | Plage | Source | Impact | À valider par |
|----|-----------|-------------------|-------|--------|--------|---------------|
| E01 | Prix électricité ENR (PV+éolien hybride) | 30 €/MWh | 22–45 | [HYP] | Très élevé | PPA, MASEN/ONEE |
| E02 | Heures pleine charge électrolyseur | 5 000 h/an | 3 500–7 500 | [HYP] ; article : 3 000–4 000 typique | Très élevé | Simulation horaire |
| E03 | Technologie d'électrolyse | PEM | AEL/PEM/SOEC | [ART] PEM majoritaire | Élevé | Fournisseurs |
| E04 | CAPEX électrolyseur | milieu Table 4 (PEM 1 750 €/kW) | 800–2 500 | [ART] (SOEC max [HYP]) | Élevé | Devis |
| E05 | Conso. système électrolyseur | 5,3 kWh/Nm³ (≈59 kWh/kg) | 5,0–5,6 (PEM) | [ART] | Élevé | Fiche technique |
| E06 | WACC / durée de vie | 8 % / 20 ans | 6–12 % / 15–25 | [HYP] | Élevé | Finance |
| E07 | Coût du CO2 | point source 50–100 $/t ; DAC 235–600 $/t | — | [ART] Table 2 | Moyen–élevé | Industriel émetteur |
| E08 | CAPEX synthèse FT (kérosène/diesel) | 1 000–1 800 €/kW_fuel | — | [HYP] (non chiffré dans l'article) | Élevé | Licencieurs FT |
| E09 | CAPEX méthanol/DME/MTG/NH3 | 300–1 200 / 600 / 1 300–2 200 €/kW_fuel | — | [ART] §4.4 | Moyen | Licencieurs |
| E10 | Utilisation / OPEX synthèse / rendement matière | 90 % / 4 % / 95 % | — | [HYP] | Moyen | EPC |
| E11 | Eau : 8,92 L/kg H2 + 25 % ; prix 2 €/m³ | 11,15 L/kg ; 2 €/m³ | 1–3 €/m³ | [ART] / [HYP] | Faible | Opérateur dessalement |
| E12 | Facteur de localisation CAPEX Maroc | 1,0 | 0,5–1,2 | [HYP] ; benchmark Chine plus bas | Élevé | Devis locaux |
| E13 | Coûts indirects / imprévus | 20 % / 15 % | — | [HYP] | Moyen | EPC |
| E14 | CAPEX ENR (PV 650, éolien 1 300 €/kW) ; facteurs de charge 30 % / 45 % | — | — | [HYP] | Moyen | Développeurs ENR |
| E15 | Prix de référence fossile (kérosène, méthanol, ammoniac…) | voir classeur | larges | [HYP] | Moyen | Cotations marché |
| E16 | Notes de la matrice de décision | 1–5 | — | [HYP] | Élevé | Atelier parties prenantes |
| E17 | Coût de production PV / éolien (LCOE) | 22 / 30 €/MWh | 15–35 / 22–45 | [HYP] | Très élevé | MASEN, développeurs |
| E18 | Charge minimale de l'électrolyseur | 10 % | 0–40 % | [HYP] ; [ART] Table 4 (flexibilité PEM/AEL) | Moyen | Fournisseurs |
| E19 | Rendement aller-retour batterie | 90 % | 85–95 % | [HYP] | Faible | Fournisseurs |
| E20 | Profils horaires PV (30 %) / éolien (45 %), latitude 28°N | synthétiques | — | [HYP] — NON mesurés | Très élevé | Séries réelles du site (ERA5, PVGIS) |

## Limites connues
- Le modèle est une pré-faisabilité (±30–50 %). Il ne chiffre ni stockage, ni réseau, ni transport, ni financement intercalaire.
- Le CAPEX annoncé en Chine (Shanxi, ~3,9 M€ par kt/an) est ~4× inférieur au modèle : vérifier le périmètre avant d'en déduire un facteur Maroc.
- Les « rendements de procédé » 59–89 % de l'article ne sont pas des rendements électricité→carburant (≈40–50 % dans le modèle).
- Contexte Maroc (ressources, OCP, ports, stratégie hydrogène) : voir feuille `Maroc_Contexte` — niveau de confiance moyen/faible, à valider.
- Simulation horaire : profils synthétiques par défaut ; sans rampes, dégradation, disponibilité ni stockage H2.
- Le prix effectif de l'électricité inclut l'énergie écrêtée (payée) : surdimensionner l'ENR augmente les heures mais aussi le prix par MWh consommé.
