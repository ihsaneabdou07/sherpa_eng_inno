# Modélisation Systémique Conceptuelle - Écosystème Énergétique Décarboné (Maroc)

## 1. Introduction et Périmètre de l'Étude
Ce document présente l'architecture fonctionnelle et conceptuelle de l'écosystème énergétique décarboné développé dans le cadre du projet de recherche en appui à la thèse (Sherpa Engineering / École Centrale Casablanca)[cite: 1, 2]. 
Le système modélisé intègre l'ensemble de la chaîne de valeur : de la production d'énergies renouvelables (photovoltaïque et éolien) et d'eau jusqu'à la synthèse de carburants décarbonés (e-fuels), en passant par le stockage et l'électrolyse[cite: 1, 4].

Le modèle conceptuel repose sur une approche modulaire indépendante des environnements de simulation lourds (hors MATLAB/Simulink), privilégiant une représentation claire des flux et des interfaces[cite: 1, 6].

---

## 2. Définition des 6 Sous-Systèmes (Blocs Fonctionnels)

L'écosystème est découpé en six grands blocs interconnectés[cite: 4] :

1. **Bloc 1 : Production d’Électricité**
   * *Technologies :* Fermes photovoltaïques (PVGIS), parcs éoliens terrestres (Global Wind Atlas), raccordement au réseau électrique national (ONEE/Grid)[cite: 1, 4].
   * *Rôle :* Fournir l'énergie électrique primaire intermittente ou garantie.

2. **Bloc 2 : Stockage d’Énergie (Batteries Stationnaires)**
   * *Technologies :* Systèmes de batteries à l'échelle du réseau (ex: Lithium-ion)[cite: 1, 4].
   * *Rôle :* Lisser l'intermittence à court terme et sécuriser l'alimentation des procédés de conversion.

3. **Bloc 3 : Traitement de l’Eau**
   * *Technologies :* Prélèvement de ressources en eau et unités de dessalement par osmose inverse (référence type Jorf Lasfar)[cite: 1, 4].
   * *Rôle :* Produire l'eau dessalée et purifiée indispensable à l'alimentation des électrolyseurs.

4. **Bloc 4 : Production d’Hydrogène**
   * *Technologies :* Électrolyseurs (Alcalin, PEM, SOEC)[cite: 1, 4].
   * *Rôle :* Combiner l'électricité (Bloc 1/2) et l'eau purifiée (Bloc 3) pour générer de l'hydrogène vert ($\text{H}_2$).

5. **Bloc 5 : Conversion & e-fuels**
   * *Technologies :* Unités de capture de $\text{CO}_2$ (industriel ou DAC), liquéfaction de l'hydrogène, et réacteurs de synthèse (procédés Fischer-Tropsch, e-méthanol, e-méthane)[cite: 1, 4].
   * *Rôle :* Transformer l'hydrogène et le $\text{CO}_2$ capté en vecteurs énergétiques liquides ou gazeux valorisables.

6. **Bloc 6 : Logistique & Usages**
   * *Technologies :* Stockage sous pression, transport par pipeline ou maritime, et satisfaction des demandes industrielles locales ou à l'export (OCP, etc.)[cite: 1, 4].
   * *Rôle :* Acheminer et distribuer les produits finaux selon les besoins de la demande.

---

## 3. Matrice des 4 Flux Inter-Blocs

Entre chacun de ces blocs, les interfaces gèrent simultanément quatre types de flux normalisés[cite: 4] :

| Interface (De $\rightarrow$ Vers) | Flux d'Énergie | Flux de Matière | Flux de Coûts | Empreinte Carbone ($\text{CO}_2$) |
| :--- | :--- | :--- | :--- | :--- |
| **Bloc 1 $\rightarrow$ Bloc 2** | Électricité intermittente ($\text{kWh}$) | N/A | Coût marginal de génération | Émissions induites par le mix EnR/Grid |
| **Bloc 1/2 $\rightarrow$ Bloc 4** | Électricité pilotée ($\text{kWh}$) | N/A | Propagation du LCOE | Suivi du contenu carbone de l'électricité |
| **Bloc 3 $\rightarrow$ Bloc 4** | N/A | Eau purifiée ($\text{m}^3$) | Coût de l'eau dessalée | Émissions liées à l'énergie du dessalement |
| **Bloc 4 $\rightarrow$ Bloc 5** | N/A | Hydrogène ($\text{kg}$) | Coût de production $\text{H}_2$ ($\text{LCOH}$) | Empreinte $\text{H}_2$ |
| **Bloc 5 $\rightarrow$ Bloc 6** | N/A | Carburants / e-fuels ($\text{kg}$ ou $\text{L}$) | Coût global de synthèse ($\text{LCOF}$) | Bilan net d'émissions (captation vs rejet) |

---

## 4. Prochaines étapes de modélisation
* Intégration des équations de dimensionnement physique dans le dossier `models/`.
* Couplage avec le module d'optimisation économique (`economics/lcoe.py`) pour minimiser le coût du carburant ($\text{LCOF}$) et l'empreinte carbone sous Python[cite: 1].