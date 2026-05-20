---
title: "Ecologie de l'informatique"
domain: "Applied Sciences"
subdomain: "Ecology"
tags: [sciences-appliquées, écologie, informatique, numérique, data-center, empreinte-carbone]
date: "2026-04-16"
---

# Ecologie de l'informatique

Le numérique représente environ **3,5 à 4 % des émissions mondiales de gaz à effet de serre** (2024), soit plus que l'aviation civile (~2,5 %). Cette empreinte croît de 6 à 9 % par an, portée par l'explosion des données, le streaming vidéo, le cloud computing et l'intelligence artificielle. Comprendre l'impact environnemental du numérique est indispensable pour tout professionnel de l'informatique.

## Répartition de l'empreinte

L'impact environnemental du numérique se répartit entre trois postes principaux :

| Poste | % des emissions | Detail |
|---|---|---|
| **Fabrication des terminaux** | ~45 % | Extraction de minerais (terres rares, cobalt, lithium), fonderie de semi-conducteurs, assemblage |
| **Usage des terminaux** | ~20 % | Consommation électrique des smartphones, PC, TV, objets connectés |
| **Data centers** | ~15-20 % | Serveurs, stockage, refroidissement |
| **Réseaux** | ~15-20 % | Antennes (4G/5G), routeurs, câbles sous-marins, fibre optique |

Le constat essentiel : **la fabrication pèse plus que l'usage**. Un smartphone neuf a déjà généré 80 % de son empreinte carbone totale avant même d'être allumé.

## Data centers

Les data centers consomment environ **1 à 1,5 % de l'électricité mondiale** (200-250 TWh/an). Leur consommation se décompose en :

| Poste | Part |
|---|---|
| **Serveurs** (calcul + stockage) | ~50 % |
| **Refroidissement** | ~30-40 % |
| **Infrastructure** (éclairage, sécurité, réseau) | ~10-15 % |

### PUE (Power Usage Effectiveness)

Le PUE mesure l'efficacité énergétique d'un data center :

```
PUE = Énergie totale du data center / Énergie consommée par les serveurs
```

| PUE | Interpretation |
|---|---|
| 1,0 | Parfait (théorique) — toute l'énergie va aux serveurs |
| 1,1-1,2 | Excellent (hyperscalers : Google, Meta, Microsoft) |
| 1,4-1,6 | Moyen (data centers classiques) |
| 2,0+ | Inefficace (ancien, mal conçu) |

### Solutions de refroidissement

| Technique | Principe | Exemple |
|---|---|---|
| **Free cooling** | Utiliser l'air extérieur quand la température le permet | Data centers en Scandinavie, Islande |
| **Immersion cooling** | Immerger les serveurs dans un liquide diélectrique non conducteur | Microsoft Project Natick (sous-marin), GRC |
| **Récupération de chaleur** | Réutiliser la chaleur des serveurs pour chauffer des bâtiments | Marne-la-Vallée (piscine chauffée par un data center) |
| **Localisation stratégique** | Installer les data centers dans des pays froids ou proches de sources d'énergie renouvelable | Google en Finlande, Meta en Suède |

## Impact de l'IA

L'intelligence artificielle a un impact énergétique croissant et préoccupant :

| Phase | Consommation |
|---|---|
| **Entraînement** | GPT-3 (2020) : ~1 300 MWh, soit l'équivalent de 120 foyers américains pendant un an. GPT-4 est estimé à 10x plus |
| **Inférence** | Chaque requête à un LLM consomme 5 à 10 fois plus qu'une recherche Google classique |
| **Eau** | L'entraînement de GPT-3 a consommé ~700 000 litres d'eau pour le refroidissement |

La course aux modèles toujours plus grands amplifie cette tendance. Les techniques de compression (quantization, distillation, pruning) permettent de réduire l'empreinte de l'inférence.

## Minerais et terres rares

Un smartphone contient plus de **50 éléments chimiques** différents. Certains posent des problèmes environnementaux et géopolitiques majeurs :

| Materiau | Usage | Problème |
|---|---|---|
| **Cobalt** | Batteries lithium-ion | 70 % de la production mondiale en RDC, conditions de travail inhumaines |
| **Lithium** | Batteries | Extraction par évaporation en Amérique du Sud (Chili, Argentine, Bolivie) — consommation d'eau massive |
| **Terres rares** (néodyme, dysprosium) | Aimants, écrans, haut-parleurs | 60 % de la production mondiale en Chine, extraction très polluante |
| **Tantale** (coltan) | Condensateurs | RDC, financement de conflits armés ("minerais de sang") |
| **Indium** | Ecrans tactiles | Ressource limitée, recyclage difficile |

Moins de **20 % des déchets électroniques** (e-waste) sont recyclés dans le monde. Le reste finit en décharge ou est exporté (souvent illégalement) vers des pays en développement (Ghana, Nigeria, Inde).

## Empreinte du quotidien numérique

| Action | Empreinte carbone approximative |
|---|---|
| Email sans pièce jointe | ~4 g CO2 |
| Email avec pièce jointe (1 Mo) | ~19 g CO2 |
| 1 heure de streaming vidéo (HD) | ~36-100 g CO2 (selon le réseau et le terminal) |
| 1 recherche Google | ~0,2 g CO2 |
| 1 requête ChatGPT | ~1-10 g CO2 (estimation) |
| Fabrication d'un smartphone | ~70 kg CO2 |
| Fabrication d'un ordinateur portable | ~300-400 kg CO2 |

Ces chiffres individuels sont faibles, mais multipliés par des milliards d'utilisateurs et des dizaines de requêtes par jour, l'impact agrégé est considérable.

## Sobriété numérique

Le concept de **sobriété numérique** (popularisé par The Shift Project en France) propose de réduire l'empreinte du numérique par des choix conscients, à tous les niveaux.

### Pour les individus

- **Allonger la durée de vie des terminaux** : c'est le levier le plus efficace. Garder son smartphone 4 ans au lieu de 2 divise son empreinte de fabrication par deux.
- Préférer le reconditionné au neuf
- Réduire le streaming vidéo (résolution adaptée, pas de lecture automatique)
- Supprimer les données inutiles (emails, photos en double, comptes inactifs)
- Désactiver la lecture automatique des vidéos sur les réseaux sociaux

### Pour les entreprises et développeurs

- **Ecoconception logicielle** : optimiser le code, réduire les requêtes inutiles, compresser les assets
- Choisir des hébergeurs alimentés en énergie renouvelable
- Dimensionner les infrastructures au besoin réel (éviter le surdimensionnement)
- Mesurer l'empreinte carbone des services numériques (outils : GreenIT Analysis, Website Carbon Calculator)
- Appliquer le principe de **frugalité des données** : ne collecter que ce qui est strictement nécessaire

### Pour les politiques publiques

- **Indice de réparabilité** (obligatoire en France depuis 2021) : note sur 10 indiquant la facilité de réparation d'un appareil
- **Loi REEN** (France, 2021) : Réduction de l'Empreinte Environnementale du Numérique — obligations de formation, d'écoconception et de collecte de données sur l'impact
- **Droit à la réparation** (directive UE 2024) : les fabricants doivent fournir des pièces détachées pendant une durée minimale
- Taxation du renouvellement prématuré des terminaux

## Références

- **The Shift Project** — *Lean ICT : pour une sobriété numérique* (2018)
- **ADEME** — études sur l'empreinte environnementale du numérique en France
- **GreenIT.fr** — *Empreinte environnementale du numérique mondial* (2019)
- **IEA** (International Energy Agency) — rapports annuels sur la consommation des data centers
