---
title: "Statistiques Descriptives (Seconde)"
domain: "Applied Sciences"
subdomain: "Mathematics > Lycée > Probabilités & Stats"
tags: [sciences-appliquées, mathématiques]
date: "2026-02-22"
---

# Statistiques Descriptives (Seconde)

> [!tip] Vue d'ensemble
> Les **statistiques descriptives** analysent des données observées pour en dégager des tendances : position centrale (moyenne, médiane) et dispersion (variance, écart-type).


# Partie I : Statistiques descriptives (Seconde)

## 1. Vocabulaire et séries statistiques

> [!important] Définitions
> - **Population** : l'ensemble des individus étudiés.
> - **Caractère** (ou variable statistique) : la propriété étudiée sur chaque individu.
>   - *Quantitatif discret* : nombre fini de valeurs (ex : nombre d'enfants).
>   - *Quantitatif continu* : valeurs dans un intervalle (ex : taille).
>   - *Qualitatif* : non numérique (ex : couleur des yeux).
> - **Effectif** $n_i$ : nombre d'individus prenant la valeur $x_i$.
> - **Fréquence** $f_i = \frac{n_i}{N}$ où $N$ est l'effectif total.

## 2. Indicateurs de position

### 2.1 Moyenne

> [!important] Définition : Moyenne
> La **moyenne** d'une série statistique $(x_1, x_2, \ldots, x_N)$ est :
> $$\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i$$
> Pour une série avec effectifs : $\bar{x} = \frac{\sum_{i=1}^{p} n_i x_i}{N}$

La moyenne est sensible aux valeurs extrêmes.

### 2.2 Médiane

> [!important] Définition : Médiane
> La **médiane** $\text{Me}$ est la valeur qui partage la série ordonnée en deux parties de même effectif :
> - Si $N$ est impair : $\text{Me} = x_{(N+1)/2}$
> - Si $N$ est pair : $\text{Me} = \frac{x_{N/2} + x_{N/2+1}}{2}$

La médiane est **robuste** : elle est peu influencée par les valeurs extrêmes.

### 2.3 Quartiles

> [!important] Définition : Quartiles
> - **Premier quartile** $Q_1$ : la plus petite valeur telle qu'au moins 25% des données lui sont inférieures ou égales.
> - **Troisième quartile** $Q_3$ : la plus petite valeur telle qu'au moins 75% des données lui sont inférieures ou égales.
> - **Écart interquartile** : $Q_3 - Q_1$ (mesure la dispersion des 50% centraux).

## 3. Indicateurs de dispersion

### 3.1 Étendue

$$\text{Étendue} = x_{\max} - x_{\min}$$

### 3.2 Variance et écart-type

> [!important] Définitions : Variance et écart-type
> La **variance** mesure la dispersion des valeurs autour de la moyenne :
> $$V(X) = \frac{1}{N}\sum_{i=1}^{N}(x_i - \bar{x})^2 = \overline{x^2} - \bar{x}^2$$
>
> L'**écart-type** est la racine carrée de la variance :
> $$\sigma = \sqrt{V(X)}$$

> [!tip] Formule de König-Huygens
> La formule $V(X) = \overline{x^2} - \bar{x}^2$ (moyenne des carrés moins carré de la moyenne) est souvent plus pratique pour le calcul.

### 3.3 Diagramme en boîte (boîte à moustaches)

Le **diagramme en boîte** résume une série statistique avec 5 valeurs :

```
Min     Q1      Me      Q3      Max
 |------|========|========|------|
        |   boîte        |
```

- Les « moustaches » vont de $x_{\min}$ à $Q_1$ et de $Q_3$ à $x_{\max}$.
- La boîte va de $Q_1$ à $Q_3$ (contient 50% des données).
- Un trait dans la boîte marque la médiane.

> [!example] Exemple
> Série : 2, 3, 5, 7, 8, 8, 9, 10, 12, 15
>
> $N = 10$, $\bar{x} = 7{,}9$
>
> Médiane : $\text{Me} = \frac{8+8}{2} = 8$
>
> $Q_1 = 5$ (valeur en position 3), $Q_3 = 10$ (valeur en position 8)
>
> Écart interquartile : $Q_3 - Q_1 = 5$

