---
title: "Programmation Dynamique"
domain: "Applied Sciences"
subdomain: "Computer Science > Algorithmique"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# Programmation Dynamique

La programmation dynamique (DP) est une technique algorithmique qui consiste à résoudre un problème en le décomposant en sous-problèmes chevauchants et en mémorisant leurs solutions pour éviter de les recalculer.

## Conditions d'applicabilité

Un problème est soluble par DP s'il possède deux propriétés :

**Sous-problèmes chevauchants** : les mêmes sous-problèmes apparaissent plusieurs fois dans la récursion. (Différent du diviser-pour-régner où les sous-problèmes sont indépendants.)

**Sous-structure optimale** : la solution optimale du problème se construit à partir des solutions optimales de ses sous-problèmes.

## Approches

### Mémoïsation (top-down)

On part de la solution récursive naïve et on ajoute un cache pour éviter de recalculer les mêmes appels.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

### Tabulation (bottom-up)

On remplit itérativement un tableau en partant des cas de base vers la solution finale.

```python
def fib(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# Optimisation espace : O(1) au lieu de O(n)
def fib_optimal(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

### Comparaison

| Critère | Mémoïsation | Tabulation |
|---|---|---|
| Direction | Top-down | Bottom-up |
| Appels inutiles | Évités naturellement | Tous calculés |
| Espace pile | O(profondeur récursion) | O(1) possible |
| Lisibilité | Proche de la récursion | Plus itératif |
| Préféré quand | Tous les sous-problèmes non nécessaires | Tous nécessaires |

## Fibonacci — exemple introductif

```
Arbre de récursion sans mémoïsation pour fib(5) :
fib(5) = fib(4) + fib(3)
fib(4) = fib(3) + fib(2)   ← fib(3) calculé deux fois
fib(3) = fib(2) + fib(1)   ← fib(2) calculé trois fois
...
Complexité naïve : O(2^n)
Avec DP : O(n)
```

## Sac à dos 0/1 (0/1 Knapsack)

**Problème** : n objets, chacun avec un poids et une valeur. Capacité maximale W. Maximiser la valeur totale sans dépasser W. Chaque objet est pris ou non (0 ou 1 fois).

```python
def sac_a_dos(poids, valeurs, capacite):
    n = len(poids)
    # dp[i][c] = valeur max avec les i premiers objets et capacité c
    dp = [[0] * (capacite + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for c in range(capacite + 1):
            # Ne pas prendre l'objet i
            dp[i][c] = dp[i - 1][c]
            # Prendre l'objet i si possible
            if poids[i - 1] <= c:
                dp[i][c] = max(dp[i][c],
                               dp[i - 1][c - poids[i - 1]] + valeurs[i - 1])

    return dp[n][capacite]

# Exemple
poids = [2, 3, 4, 5]
valeurs = [3, 4, 5, 6]
capacite = 8
print(sac_a_dos(poids, valeurs, capacite))  # 10
```

Complexité : O(n · W) en temps, O(n · W) en espace (optimisable à O(W) avec un seul tableau 1D).

## Plus longue sous-séquence commune (LCS)

**Problème** : trouver la plus longue sous-séquence (pas forcément contiguë) commune à deux chaînes.

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruction de la séquence
    seq = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            seq.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return ''.join(reversed(seq)), dp[m][n]

print(lcs("ABCBDAB", "BDCAB"))  # ('BCAB', 4)
```

Complexité : O(m · n).

## Plus longue sous-séquence croissante (LIS)

**Problème** : trouver la plus longue sous-séquence strictement croissante d'un tableau.

```python
# Approche DP naïve — O(n²)
def lis_naive(arr):
    n = len(arr)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if arr[j] < arr[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

# Approche optimisée avec recherche binaire — O(n log n)
import bisect

def lis_optimal(arr):
    sous_seq = []
    for x in arr:
        pos = bisect.bisect_left(sous_seq, x)
        if pos == len(sous_seq):
            sous_seq.append(x)
        else:
            sous_seq[pos] = x
    return len(sous_seq)
```

## Chemin dans une grille

**Problème** : trouver le nombre de chemins distincts d'un coin à l'autre d'une grille m×n (uniquement droite et bas).

```python
def nb_chemins(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]

# Variante : chemin de coût minimal
def chemin_minimal(grille):
    m, n = len(grille), len(grille[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grille[0][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j - 1] + grille[0][j]
    for i in range(1, m):
        dp[i][0] = dp[i - 1][0] + grille[i][0]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = min(dp[i - 1][j], dp[i][j - 1]) + grille[i][j]
    return dp[m - 1][n - 1]
```

## Découpe de tige (Rod Cutting)

**Problème** : une tige de longueur n, prix[i] pour une pièce de longueur i. Maximiser le revenu total.

```python
def decoupe_tige(prix, n):
    dp = [0] * (n + 1)
    for longueur in range(1, n + 1):
        for coupe in range(1, longueur + 1):
            dp[longueur] = max(dp[longueur],
                               prix[coupe - 1] + dp[longueur - coupe])
    return dp[n]
```

## Distance d'édition (Edit Distance / Levenshtein)

**Problème** : nombre minimal d'opérations (insertion, suppression, substitution) pour transformer s1 en s2.

```python
def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],    # suppression
                                    dp[i][j - 1],    # insertion
                                    dp[i - 1][j - 1]) # substitution
    return dp[m][n]

print(edit_distance("kitten", "sitting"))  # 3
```

## Méthode générale pour résoudre un problème DP

1. Identifier si le problème a des sous-problèmes chevauchants et une sous-structure optimale
2. Définir l'état : qu'est-ce que dp[i] (ou dp[i][j]) représente ?
3. Écrire la relation de récurrence
4. Identifier les cas de base
5. Choisir top-down ou bottom-up
6. Optimiser l'espace si possible (souvent un tableau 1D suffit au lieu de 2D)

## Problèmes classiques supplémentaires

| Problème | État dp | Récurrence |
|---|---|---|
| Coin Change | dp[m] = min pièces pour montant m | dp[m] = min(dp[m - piece] + 1) |
| Partition égale | dp[s] = atteignable avec somme s | dp[s] = dp[s] or dp[s - num] |
| Sous-tableau de somme max (Kadane) | dp[i] = max somme finissant en i | dp[i] = max(arr[i], dp[i-1] + arr[i]) |
| Parenthésage matriciel | dp[i][j] = coût min de multiplication | min sur k de dp[i][k] + dp[k+1][j] + coût |
