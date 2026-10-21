# Note d'innovation — module e-fuels (Sherpa Engineering)

*Prototype d'aide à la décision pour un écosystème énergétique décarboné au Maroc (PV, éolien, stockage, dessalement, électrolyse, carburants de synthèse).*

**Statut : pré-faisabilité (±30–50 %). Les valeurs marquées [HYP] sont des hypothèses non validées par des données Maroc.**
Source scientifique : Colelli et al. (2026), *Energy Conversion and Management*, doi:10.1016/j.enconman.2025.120529 [ART].

---

## 1. Problème traité

Une entreprise qui envisage de produire des e-fuels au Maroc doit répondre à quatre questions : **quel produit**, **à quel coût**, **avec quelle taille d'installation**, **et avec quels risques**. L'article de référence donne des fourchettes issues de sources hétérogènes ; il ne dit pas ce que cela donne pour un site marocain, ni comment arbitrer entre produits.

## 2. Ce que le module apporte

| # | Contribution | Fichiers | Nature de l'apport |
|---|--------------|----------|--------------------|
| 1 | **Base de connaissances condensée et sourcée** : 6 e-fuels, 3 procédés, 35 projets mondiaux, électrolyseurs, captage CO2, politiques, certification SAF | `efuels_maroc_base_donnees.xlsx`, CSV | Synthèse, traçabilité [ART]/[HYP]/[CALC] |
| 2 | **Modèle de coût reproductible** (Excel, Python, R) donnant coût €/t, €/MWh, efficacité, eau, part de l'hydrogène | `efuel_economics.py`, `Calculateur_LCOE`, `efuels_analysis.Rmd` | Outil, vérifié par recoupement Excel = Python |
| 3 | **Couplage simulation horaire → prix effectif → coût** : l'énergie écrêtée est payée, donc surdimensionner l'ENR gagne des heures mais augmente le prix par MWh consommé | `hourly_sim.py`, `simulation_horaire.xlsx`, `efuels_page.py` | Méthode d'arbitrage propre au projet |
| 4 | **Dimensionnement et interfaces** vers les autres modules (eau dessalée, MW ENR, charge électrique moyenne, CO2/jour) | `capex_data.xlsx` (Dimensionnement) | Intégration au prototype |
| 5 | **Matrice de décision pondérée** (poids et notes modifiables) | `Matrice_Decision` | Aide à la décision en atelier |
| 6 | **Registre d'hypothèses et alertes qualité** | `HYPOTHESES_EFUEL.md`, `Alertes_qualite` | Rigueur et traçabilité |
| 7 | **Pistes d'innovation** ancrées dans l'article (14) | `Opportunites_Innovation` | Feuille de route |

**Ce qui est nouveau pour l'entreprise** : une capacité de calcul et de décision réutilisable sur les e-fuels, branchée sur l'écosystème énergétique du prototype. **Ce n'est pas une nouveauté scientifique** : les méthodes (LCOH, facteur de recouvrement, bilan stœchiométrique, simulation horaire) sont classiques ; la valeur est dans l'intégration, la traçabilité et l'adaptation au contexte.

## 3. Constats utiles que la base permet de faire

1. **Le prix de l'électricité et les heures de charge dominent le coût** : l'hydrogène représente ≈ 80–86 % du coût de production dans le modèle.
2. **Les rendements de l'article (59–89 %) ne sont pas des rendements électricité→carburant** : ils portent sur la conversion seule ; la chaîne complète donne ≈ 43–47 % dans le modèle.
3. **L'hypothèse « 30 €/MWh et 5 000 h » est légèrement optimiste** : avec des profils synthétiques (300 MW PV, 200 MW éolien, 250 MW d'électrolyseur), la simulation donne ≈ 5 030 h, 20 % d'écrêtage, ≈ 32,6 €/MWh effectifs et un LCOH de ≈ 4,83 €/kg contre 4,70 €/kg.
4. **Écart avec un projet chinois** : le CAPEX annoncé de Shanxi (≈ 3,9 M€ par kt/an) est ≈ 4 fois inférieur au modèle ; le périmètre du chiffre annoncé est à vérifier avant d'en tirer un facteur Maroc.
5. **Anomalie de source repérée** : la réf. [320], citée pour le CO2 biogénique du Brésil (Table 6), porte sur des schistes ; ces hypothèses sont à vérifier avant réemploi.

## 4. Résultats préliminaires (hypothèses par défaut)

*30 €/MWh, 5 000 h/an, PEM, CO2 de point source, WACC 8 %, durée de vie 20 ans.*

| Produit | Coût (€/t) | Efficacité élec.→carburant | Score matrice (1–5) |
|---------|-----------:|---------------------------:|--------------------:|
| e-ammoniac | ≈ 1 050 | ≈ 46 % | 4,4 |
| e-méthanol | ≈ 1 120 | ≈ 45 % | 3,4 |
| e-kérosène | ≈ 2 690 | ≈ 43 % | 3,0 |
| e-diesel | ≈ 2 690 | ≈ 43 % | 2,5 |
| e-DME | ≈ 1 550 | ≈ 47 % | 2,2 |
| e-essence | ≈ 2 500 | ≈ 43 % | 2,2 |

LCOH ≈ 4,7 €/kg (article : 3–6 €/kg). Usine de 100 kt/an d'e-méthanol : ≈ 234 MW d'électrolyse, ≈ 720 M€ de CAPEX hors ENR (≈ 1 070 M€ avec ENR équivalente).

**Lecture prudente** : les notes de la matrice sont un jugement préliminaire [HYP]. Elles orientent vers l'**e-ammoniac** (pas de CO2 requis, demande locale potentielle) et l'**e-méthanol** (voie mature, usage maritime), à confirmer par des données du site et un atelier avec les parties prenantes. L'e-kérosène reste pertinent pour l'export vers l'UE mais coûte nettement plus cher et exige plus de CO2.

## 5. Limites (à dire clairement)

- Les **profils horaires** par défaut sont **synthétiques** : aucun site réel n'a été simulé.
- Le contexte Maroc (ressources, OCP, ports, stratégie hydrogène) est de **confiance moyenne à faible** ; voir `Maroc_Contexte`.
- Le modèle ne chiffre ni stockage d'hydrogène, ni réseau, ni terrain, ni transport, ni financement intercalaire, ni remplacement des stacks.
- Les coûts de l'article proviennent de sources hétérogènes ; le CAPEX Fischer–Tropsch est une hypothèse (non chiffré dans l'article).
- Le fichier R Markdown et l'affichage Streamlit n'ont pas été exécutés dans l'environnement de génération ; la logique Python est testée (17 tests).

## 6. Prochaines étapes (par priorité)

1. **Remplacer les profils synthétiques par des séries réelles** d'un ou deux sites candidats (ERA5, PVGIS, mesures) et relancer la simulation.
2. **Obtenir des offres de prix** : électricité ENR (PPA), électrolyseur, captage CO2, unité de synthèse ; remplacer les valeurs [HYP] du registre.
3. **Cartographier les sources de CO2** (cimenteries, centrales, biogénique) et la demande locale (ammoniac).
4. **Atelier de décision** pour revoir poids et notes de la matrice avec direction, ingénierie et finance.
5. **Brancher le module aux autres modules** du prototype (dessalement, PV/éolien, stockage, optimisation) via les sorties « Interface » du dimensionnement.
6. **Étendre le modèle** : stockage d'hydrogène, rampes, dégradation, flux de trésorerie (VAN, TRI) et analyse de risque (Monte-Carlo).

## 7. Reproduire les résultats

```
pip install streamlit pandas numpy openpyxl pytest
python -m pytest tests/
streamlit run app/efuels_page.py
```
Excel : modifier les cellules bleues de `Calculateur_LCOE`, `simulation_horaire.xlsx` et `capex_data.xlsx` (Parametres).
