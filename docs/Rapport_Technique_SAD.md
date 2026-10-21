# Rapport Technique : Système d'Aide à la Décision (SAD) Multicritère pour un Écosystème Hydrogène Vert et E-Fuels à Laâyoune

---

## 1. Introduction & Contexte du Projet
Dans le cadre de la transition énergétique et de la stratégie nationale de valorisation des énergies renouvelables, ce projet vise à concevoir un **Système d'Aide à la Décision (SAD) multicritère** pour un écosystème industrialo-énergétique intégré situé à **Laâyoune, Maroc**. 

L'objectif est de modéliser l'ensemble de la chaîne de valeur : de la production d'électricité décarbonée (Solaire PV et Éolien) et du stockage stationnaire, jusqu'à la production d'hydrogène vert par électrolyse PEM, le dessalement de l'eau de mer, et la synthèse d'e-carburants (e-méthanol) via la valorisation de $\text{CO}_2$.

---

## 2. Architecture du Modèle et Méthodologie
Le modèle repose sur une simulation horaire rigoureuse sur une année complète (**8760 heures**), calibrée sur les gisements et conditions climatiques du site côtier de Laâyoune.

### Les 4 Piliers d'Évaluation du SAD :
1. **Pilier Économique :** Minimisation du $\text{LCOH}$ (Levelized Cost of Hydrogen) et du $\text{LCOM}$ (Levelized Cost of Methanol).
2. **Pilier Environnemental :** Maximisation de l'efficience des énergies renouvelables et minimisation du gaspillage (*curtailment*).
3. **Pilier Technique :** Adéquation étroite avec la cible de production industrielle fixée.
4. **Pilier Faisabilité & Compromis Global :** Équilibre multicritère combinant CAPEX, OPEX et robustesse opérationnelle.

---

## 3. Description des Blocs Technologiques de la Chaîne de Valeur

* **Bloc EnR & Stockage (Batteries LFP) :** Intégration d'une ferme photovoltaïque, d'une ferme éolienne et de batteries stationnaires LiFePO₄ (efficacité de conversion *round-trip* de 90%) pour lisser l'intermittence, sécuriser l'alimentation de l'électrolyseur et réduire les pertes énergétiques.
* **Bloc Eau (Dessalement SWRO) :** Unité d'osmose inverse dimensionnée sur la base des données régionales (nécessitant environ $9\text{ L}$ d'eau ultrapure par kg d' $\text{H}_2$), avec un CAPEX unitaire de $\approx 1\,270\text{ €/(m}^3\text{/jour)}$ et une consommation électrique de $3,5\text{ kWh/m}^3$.
* **Bloc Électrolyse PEM :** Conversion de l'eau et de l'électricité en hydrogène vert haute pureté.
* **Bloc E-Fuels (E-Méthanol) :** Unité de capture de $\text{CO}_2$ et réacteur de synthèse chimique combinant $\text{CO}_2$ et $\text{H}_2$ selon la stœchiométrie de référence ($\approx 0,189\text{ t H}_2$ et $\approx 1,374\text{ t CO}_2$ par tonne d'e-méthanol).

---

## 4. Résultats Chiffrés de l'Écosystème Intégré

Après exécution de l'algorithme d'optimisation multicritère intégrant l'ensemble des contraintes (EnR, Stockage, Eau et E-Fuels), la configuration optimale retenue est la suivante :

### ⚙️ Configuration Optimale du Complexe :
* **Puissance PV Solaire :** $200,0\text{ MW}$
* **Puissance Éolien Terrestre :** $80,0\text{ MW}$
* **Puissance Électrolyseur PEM :** $90,0\text{ MW}$
* **Capacité de Stockage (Batteries) :** $50,0\text{ MWh}$

### 📈 Performances Industrielles et Économiques :
* **Production d'Hydrogène Vert :** $14\,032\text{ tonnes/an}$
* **Production d'E-Méthanol :** $74\,245\text{ tonnes/an}$ (requérant $65\,801\text{ t de CO}_2\text{/an}$)
* **$\text{LCOH}$ Global (incluant le dessalement) :** $3,91\text{ €/kg}$
* **Coût de revient de l'E-Méthanol ($\text{LCOM}$) :** **$738\text{ €/tonne}$** (soit $0,74\text{ €/kg}$)
* **CAPEX Global du Complexe :** $319,1\text{ M€}$

---

## 5. Conclusion & Perspectives
Ce modèle démontre la viabilité technico-économique remarquable d'un écosystème de power-to-x à Laâyoune. L'ajout du stockage par batteries stationnaires permet d'optimiser le facteur de charge de la chaîne de synthèse et d'atteindre un coût de l'e-méthanol très compétitif de **$738\text{ €/t}$**. 

*Perspectives :* Extension de la démarche vers une modélisation architecturale systémique formelle (approche MBSE / SysML / Capella).