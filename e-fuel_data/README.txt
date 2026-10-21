=====================================================================
 MODULE E-FUELS — SHERPA ENGINEERING
 Prototype d'aide à la décision : écosystème énergétique décarboné
 du Maroc (PV, éolien, stockage, dessalement, électrolyse,
 carburants de synthèse)
=====================================================================

1. OBJECTIF
-----------
Fournir à l'entreprise une base de connaissances et un modèle de
pré-faisabilité sur les carburants électro-synthétiques LIQUIDES
(e-kérosène, e-diesel, e-méthanol, e-DME, e-essence, e-ammoniac) afin
d'aider à choisir : quel produit, quelle voie, quelle taille, quels
risques, et quelles pistes d'innovation.

2. SOURCES ET STATUT DES DONNÉES
--------------------------------
[ART] Colelli L., Dell'Aversano S., Bassano C., Vanga G., Gallucci K.,
      Vilardi G. (2026). "Liquid e-fuels for a sustainable future: a
      comprehensive review of production, regulation, and technological
      innovation". Energy Conversion and Management.
      doi:10.1016/j.enconman.2025.120529
[HYP] Hypothèse Sherpa / connaissance générale, NON issue de l'article.
      À valider avec des données Maroc (devis, PPA, mesures de site).
[CALC] Valeur calculée par formule.
Toutes les cellules jaunes des classeurs sont des hypothèses [HYP].

3. CONTENU DU LIVRABLE
----------------------
efuels_maroc_base_donnees.xlsx   Classeur condensé (19 feuilles) :
    Synthese_cles, Voies_procedes, Produits, Electrolyse, Capture_CO2,
    Azote_H2_Eau_Elec, Projets_35, LCOE_pays, Politiques_regl,
    Barrieres_Risques, Maroc_Contexte [HYP], Opportunites_Innovation,
    Calculateur_LCOE, Sensibilite, Matrice_Decision,
    Hypotheses_Registre, Alertes_qualite, Sources
capex_data.xlsx                  CAPEX (électrolyseurs, synthèse, CO2),
    benchmarks de projets, dimensionnement de 6 usines e-fuels à la même
    capacité, scénarios de CAPEX, bloc "Interface" vers les autres
    modules (eau, ENR, charge électrique).
    NB : livré en .xlsx. Pour le format .xlsb : ouvrir dans Excel >
    Fichier > Enregistrer sous > "Classeur Excel binaire (*.xlsb)".
efuels_analysis.Rmd              Rapport R Markdown reproductible.
efuel_economics.py               Module Python (même logique que le
    Calculateur_LCOE) à placer dans economics/.
test_efuel_economics.py          Tests (pytest) à placer dans tests/.
efuels_params.yaml               Paramètres par défaut -> config/.
HYPOTHESES_EFUEL.md              Registre des hypothèses -> racine/docs.
data_efuels_csv.zip              6 tables CSV (séparateur ";", UTF-8)
    -> data/efuels/ (projets, électrolyseurs, captage CO2, LCOE pays,
    voies de procédés, synthèse).
README.txt                       Ce fichier.

4. PLACEMENT DANS LE DÉPÔT GITHUB
---------------------------------
    data/efuels/efuels_maroc_base_donnees.xlsx
    data/efuels/capex_data.xlsx
    data/efuels/*.csv                (contenu du zip)
    economics/efuel_economics.py     (+ economics/__init__.py vide)
    config/efuels_params.yaml
    tests/test_efuel_economics.py
    docs/efuels_analysis.Rmd
    docs/README_efuels.txt           (ce fichier)
    HYPOTHESES_EFUEL.md              (ou fusionner dans HYPOTHESES.md)

5. UTILISATION
--------------
Excel
  1) Calculateur_LCOE : modifier les cellules BLEUES (prix électricité,
     heures de charge, technologie, type de CO2, WACC...).
  2) Lire la table F (coût €/t, €/MWh, efficacité, eau, part H2).
  3) Sensibilite : grilles LCOH et coût produit.
  4) Matrice_Decision : ajuster poids et notes avec les parties
     prenantes ; le classement se met à jour.
  5) capex_data.xlsx > Parametres puis Dimensionnement.
Python
     from economics.efuel_economics import Params, product_cost
     product_cost(Params(elec_price_eur_mwh=25, flh=6000), "e-ammonia")
     python -m pytest tests/test_efuel_economics.py
     (variable EFUELS_XLSX=chemin du classeur pour la vérification croisée)
R
     rmarkdown::render("docs/efuels_analysis.Rmd",
        params = list(xlsx_path = "data/efuels/efuels_maroc_base_donnees.xlsx"))
     Paquets : readxl, dplyr, tidyr, ggplot2, knitr, scales.
     (Le Rmd n'a pas été exécuté dans l'environnement de génération :
      à tester localement.)

6. RÉSULTATS PAR DÉFAUT (illustratifs)
--------------------------------------
Hypothèses : 30 EUR/MWh, 5 000 h/an, PEM, CO2 point source, WACC 8 %.
  LCOH ~ 4,7 EUR/kg H2 (article : 3-6 EUR/kg)
  e-méthanol ~ 1 120 EUR/t ; e-ammoniac ~ 1 050 EUR/t ;
  e-kérosène ~ 2 690 EUR/t ; efficacité électricité->carburant 43-47 %.
  Usine 100 kt/an e-méthanol : ~234 MW d'électrolyse, ~720 MEUR de
  CAPEX hors ENR (~1 070 MEUR avec ENR équivalente).
Ces chiffres sont des ordres de grandeur de pré-faisabilité (+/-30-50 %)
et dépendent surtout du prix de l'électricité et des heures de charge.

7. LIMITES À CONNAÎTRE
----------------------
- Le modèle ne chiffre pas : stockage, réseau, terrain, transport,
  financement intercalaire, taxes, remplacement des stacks.
- Les "rendements de procédé" 59-89 % de l'article portent sur la
  conversion seule, pas sur la chaîne électricité->carburant.
- Le CAPEX chinois annoncé (Shanxi) est ~4x inférieur au modèle :
  vérifier le périmètre avant d'en tirer un facteur de localisation.
- La feuille Maroc_Contexte est à confiance moyenne/faible : valider.
- Les données datent de l'article (2024-2025) ; revérifier prix et
  réglementation (RFNBO, ReFuelEU, CBAM) avant décision.
- Voir la feuille Alertes_qualite (incohérences relevées dans l'article).

8. GLOSSAIRE
------------
AEL/PEM/SOEC : électrolyse alcaline / à membrane polymère / oxyde solide
FT : Fischer-Tropsch · MTG : méthanol vers essence · DAC : captage direct
dans l'air · RFNBO : carburants renouvelables d'origine non biologique
SAF : carburant d'aviation durable · LCOH : coût actualisé de l'hydrogène
PCI : pouvoir calorifique inférieur · CRF : facteur de recouvrement du
capital · TRL : niveau de maturité technologique · ASU : unité de
séparation de l'air.
