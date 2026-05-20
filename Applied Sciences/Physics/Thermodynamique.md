---
title: "Thermodynamique"
domain: "Applied Sciences"
subdomain: "Physics"
tags: [sciences-appliquées, physique]
date: "2026-02-04"
---
# Thermodynamique

## Vue d'ensemble

La **thermodynamique** est l'étude des transferts d'énergie et de chaleur, et de leurs effets sur la matière. Elle repose sur quatre lois fondamentales qui gouvernent l'univers.


## Les quatre lois de la thermodynamique

### Loi zéro : Équilibre thermique

**Si A est en équilibre avec B, et B avec C, alors A est en équilibre avec C.**

- Permet de définir la température
- Base des thermomètres

### Première loi : Conservation de l'énergie

**L'énergie ne se crée ni ne se détruit, elle se transforme.**

```
ΔU = Q - W
```

- ΔU : variation d'énergie interne
- Q : chaleur reçue
- W : travail fourni

**Équivalent** : E_totale = constante

### Deuxième loi : Entropie

**L'entropie d'un système isolé ne peut qu'augmenter (ou rester constante).**

```
ΔS ≥ 0
```

**Formulations** :

**Clausius** : La chaleur ne passe spontanément que du chaud au froid

**Kelvin** : Impossible de convertir intégralement la chaleur en travail

**Conséquences** :
- Flèche du temps (irréversibilité)
- Dégradation de l'énergie
- Mort thermique de l'univers

**Entropie** :
```
S = k ln Ω
```
- k : constante de Boltzmann
- Ω : nombre de micro-états

**Interprétation statistique** : Mesure du désordre

### Troisième loi : Zéro absolu

**Il est impossible d'atteindre le zéro absolu (0 K = -273,15°C) en un nombre fini d'opérations.**

**Au zéro absolu** :
- S = 0 (cristal parfait)
- Mouvement thermique nul


## Concepts fondamentaux

### Température

**Mesure de l'agitation thermique**

**Échelles** :
- Celsius : °C
- Kelvin : K (absolue)
- Fahrenheit : °F

**Conversions** :
- K = °C + 273,15
- °F = °C × 9/5 + 32

### Chaleur (Q)

**Transfert d'énergie thermique**

**Modes de transfert** :
1. **Conduction** : Contact direct (métaux)
2. **Convection** : Déplacement de fluide (eau bouillante)
3. **Rayonnement** : Ondes EM (Soleil)

**Capacité thermique** :
```
Q = mcΔT
```
- m : masse
- c : capacité thermique massique
- ΔT : variation de température

### Travail (W)

**Transfert d'énergie mécanique**

```
W = ∫ P dV
```
- P : pression
- V : volume

### Énergie interne (U)

**Somme des énergies microscopiques (cinétique + potentielle)**

**Gaz parfait** :
```
U = (3/2) nRT
```

### Enthalpie (H)

**H = U + PV**

- Utile pour transformations à pression constante
- Chaleur de réaction chimique

### Énergie libre de Gibbs (G)

**G = H - TS**

- Prédit spontanéité des réactions
- ΔG < 0 : réaction spontanée
- ΔG = 0 : équilibre


## Machines thermiques

### Moteur thermique

**Convertit chaleur en travail**

**Rendement** :
```
η = W / Q_chaud
```

**Cycle de Carnot** (idéal) :
```
η_Carnot = 1 - T_froid / T_chaud
```

**Exemples** :
- Moteur à combustion
- Centrale thermique
- Machine à vapeur

### Réfrigérateur / Pompe à chaleur

**Transfert chaleur du froid au chaud (avec travail)**

**Coefficient de performance (COP)** :
```
COP = Q_froid / W
```

**Réfrigérateur de Carnot** :
```
COP_Carnot = T_froid / (T_chaud - T_froid)
```


## Gaz parfait

### Équation d'état

```
PV = nRT
```

- P : pression
- V : volume
- n : quantité de matière (mol)
- R : constante des gaz parfaits (8,314 J·mol⁻¹·K⁻¹)
- T : température

### Transformations

**Isotherme** (T = cste) :
- PV = cste

**Isobare** (P = cste) :
- V/T = cste

**Isochore** (V = cste) :
- P/T = cste

**Adiabatique** (Q = 0) :
- PV^γ = cste
- γ = C_p / C_v


## Entropie et désordre

### Interprétation statistique (Boltzmann)

**S = k ln Ω**

- Plus de micro-états = plus d'entropie
- Système évolue vers l'état le plus probable

**Exemple** :
- Gaz dans un coin : peu probable (faible S)
- Gaz réparti uniformément : probable (forte S)

### Flèche du temps

**L'entropie explique pourquoi le temps semble avoir une direction.**

- Passé : faible entropie
- Futur : haute entropie
- Verre brisé ne se reconstruit pas spontanément

### Mort thermique de l'univers

**Hypothèse** :
- L'univers tend vers l'équilibre thermique
- Entropie maximale
- Plus de travail possible
- Température uniforme


## Applications

### Ingénierie

- Moteurs (voitures, avions)
- Centrales électriques
- Climatisation, réfrigération

### Chimie

- Thermochimie (réactions)
- Équilibres chimiques
- Enthalpie de formation

### Biologie

- Métabolisme (ATP)
- Homéostasie (température corporelle)

### Informatique

- Refroidissement des processeurs
- Limites thermodynamiques du calcul

### Cosmologie

- Big Bang (entropie initiale faible)
- Trous noirs (entropie gigantesque)


## Grands scientifiques

**Sadi Carnot** (1796-1832) : Cycle de Carnot, rendement maximal

**Rudolf Clausius** (1822-1888) : Concept d'entropie

**William Thomson (Lord Kelvin)** (1824-1907) : Échelle absolue de température

**Ludwig Boltzmann** (1844-1906) : Interprétation statistique

**Josiah Willard Gibbs** (1839-1903) : Énergie libre, thermodynamique chimique

**James Clerk Maxwell** (1831-1879) : Distribution des vitesses, démon de Maxwell


## Paradoxes et questions

### Démon de Maxwell

**Créature hypothétique qui trie les molécules rapides et lentes**

- Semble violer la 2e loi
- Résolution : information = entropie

### Flèche du temps

- Pourquoi l'entropie était-elle faible au Big Bang ?
- Condition initiale ou loi physique ?

### Trous noirs

- Entropie proportionnelle à la surface (pas au volume !)
- S = k A / (4 l_p²)
- Lien avec gravité quantique


## Liens connexes

- [[Mécanique quantique]] - Thermodynamique quantique
- [[../Chemistry/Chimie]] - Thermochimie
- [[Mécanique statistique]] - Fondements microscopiques


## Ressources

**Livres** :
- "Thermodynamique" - José-Philippe Pérez
- "Thermodynamics and Statistical Mechanics" - Greiner
- "The Laws of Thermodynamics: A Very Short Introduction" - Peter Atkins

**Cours** :
- MIT OCW : 5.60 Thermodynamics & Kinetics
- Khan Academy : Thermodynamics


*Créé le : 2026-01-01*  
*Dernière mise à jour : 2026-01-01*
