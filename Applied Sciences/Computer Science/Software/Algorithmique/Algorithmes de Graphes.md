---
title: "Algorithmes de Graphes"
domain: "Applied Sciences"
subdomain: "Computer Science > Algorithmique"
tags: [sciences-appliquées, informatique]
date: "2026-02-24"
---

# Algorithmes de Graphes

Les graphes modélisent des relations entre entités : réseaux sociaux, cartes routières, internet, dépendances logicielles. Maîtriser leurs algorithmes est fondamental en informatique.

## Rappel : types de graphes

| Type | Description | Exemple |
|---|---|---|
| Non orienté | Les arêtes sont bidirectionnelles | Réseau d'amis |
| Orienté (digraphe) | Les arêtes ont une direction | Web, Twitter |
| Pondéré | Les arêtes ont un poids | Cartes routières |
| Acyclique | Pas de cycle | Arbre, DAG |
| DAG | Directed Acyclic Graph | Dépendances, compilation |

## BFS — Breadth-First Search

Explore les sommets couche par couche, en utilisant une file. Trouve le plus court chemin en termes de nombre d'arêtes (graphes non pondérés).

```python
from collections import deque

def bfs(graphe, depart):
    visites = set()
    file = deque([depart])
    visites.add(depart)
    ordre = []

    while file:
        sommet = file.popleft()
        ordre.append(sommet)
        for voisin in graphe[sommet]:
            if voisin not in visites:
                visites.add(voisin)
                file.append(voisin)
    return ordre

def bfs_chemin(graphe, depart, arrivee):
    """Retourne le plus court chemin (en nombre d'arêtes)."""
    file = deque([(depart, [depart])])
    visites = {depart}
    while file:
        sommet, chemin = file.popleft()
        if sommet == arrivee:
            return chemin
        for voisin in graphe[sommet]:
            if voisin not in visites:
                visites.add(voisin)
                file.append((voisin, chemin + [voisin]))
    return None
```

Complexité : O(V + E) en temps et en espace. V sommets, E arêtes.

Usage : plus court chemin (arêtes non pondérées), exploration par couches, vérification de connexité, bipartisme.

## DFS — Depth-First Search

Explore aussi loin que possible avant de revenir en arrière. Utilise une pile (ou la récursion).

```python
def dfs_recursif(graphe, sommet, visites=None):
    if visites is None:
        visites = set()
    visites.add(sommet)
    print(sommet)
    for voisin in graphe[sommet]:
        if voisin not in visites:
            dfs_recursif(graphe, voisin, visites)
    return visites

def dfs_iteratif(graphe, depart):
    visites = set()
    pile = [depart]
    ordre = []
    while pile:
        sommet = pile.pop()
        if sommet not in visites:
            visites.add(sommet)
            ordre.append(sommet)
            for voisin in reversed(graphe[sommet]):
                if voisin not in visites:
                    pile.append(voisin)
    return ordre
```

Complexité : O(V + E).

Usage : détection de cycles, tri topologique, composantes fortement connexes, résolution de labyrinthes.

## Algorithme de Dijkstra

Trouve le plus court chemin depuis un sommet source vers tous les autres, dans un graphe à poids positifs.

```python
import heapq

def dijkstra(graphe, depart):
    """graphe : dict {sommet: [(voisin, poids), ...]}"""
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {sommet: None for sommet in graphe}
    tas = [(0, depart)]  # (distance, sommet)

    while tas:
        dist_actuelle, sommet = heapq.heappop(tas)
        if dist_actuelle > distances[sommet]:
            continue  # chemin obsolète
        for voisin, poids in graphe[sommet]:
            distance = dist_actuelle + poids
            if distance < distances[voisin]:
                distances[voisin] = distance
                predecesseurs[voisin] = sommet
                heapq.heappush(tas, (distance, voisin))

    return distances, predecesseurs

def reconstruire_chemin(predecesseurs, arrivee):
    chemin = []
    while arrivee is not None:
        chemin.append(arrivee)
        arrivee = predecesseurs[arrivee]
    return list(reversed(chemin))
```

Complexité : O((V + E) log V) avec un tas binaire.

Limitation : ne fonctionne pas avec des poids négatifs.

## Algorithme de Bellman-Ford

Gère les poids négatifs. Détecte les cycles négatifs.

```python
def bellman_ford(sommets, aretes, source):
    """aretes : liste de (u, v, poids)"""
    distances = {s: float('inf') for s in sommets}
    distances[source] = 0

    for _ in range(len(sommets) - 1):
        for u, v, poids in aretes:
            if distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids

    # Détection de cycle négatif
    for u, v, poids in aretes:
        if distances[u] + poids < distances[v]:
            raise ValueError("Cycle négatif détecté")

    return distances
```

Complexité : O(V · E). Plus lent que Dijkstra mais plus général.

## Floyd-Warshall

Calcule les plus courts chemins entre toutes les paires de sommets.

```python
def floyd_warshall(matrice):
    """matrice[i][j] = poids de l'arête i→j, float('inf') si absente."""
    n = len(matrice)
    dist = [row[:] for row in matrice]

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist
```

Complexité : O(V³). Usage : graphes denses, nécessité de toutes les paires.

## Arbre couvrant minimal (MST)

### Algorithme de Prim

Construit le MST en ajoutant à chaque étape l'arête de poids minimal reliant l'arbre à un sommet non encore inclus.

```python
def prim(graphe, depart):
    visites = {depart}
    aretes_mst = []
    tas = [(poids, depart, voisin) for voisin, poids in graphe[depart]]
    heapq.heapify(tas)

    while tas and len(visites) < len(graphe):
        poids, u, v = heapq.heappop(tas)
        if v not in visites:
            visites.add(v)
            aretes_mst.append((u, v, poids))
            for voisin, p in graphe[v]:
                if voisin not in visites:
                    heapq.heappush(tas, (p, v, voisin))
    return aretes_mst
```

Complexité : O(E log V) avec un tas.

### Algorithme de Kruskal

Trie toutes les arêtes par poids et les ajoute si elles ne créent pas de cycle (Union-Find).

```python
def kruskal(sommets, aretes):
    aretes.sort(key=lambda x: x[2])
    parent = {s: s for s in sommets}

    def trouver(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]  # compression de chemin
            x = parent[x]
        return x

    def unir(x, y):
        parent[trouver(x)] = trouver(y)

    mst = []
    for u, v, poids in aretes:
        if trouver(u) != trouver(v):
            unir(u, v)
            mst.append((u, v, poids))
    return mst
```

Complexité : O(E log E). Mieux adapté aux graphes creux.

## Tri topologique

Ordonne les sommets d'un DAG de façon que tout arc (u, v) place u avant v. Utilisé pour les dépendances, la compilation, la planification de tâches.

```python
def tri_topologique(graphe):
    visites = set()
    ordre = []

    def dfs(sommet):
        visites.add(sommet)
        for voisin in graphe.get(sommet, []):
            if voisin not in visites:
                dfs(voisin)
        ordre.append(sommet)

    for sommet in graphe:
        if sommet not in visites:
            dfs(sommet)
    return list(reversed(ordre))
```

## Détection de cycles

### Dans un graphe non orienté (DFS)

```python
def a_cycle_non_oriente(graphe):
    visites = set()

    def dfs(sommet, parent):
        visites.add(sommet)
        for voisin in graphe[sommet]:
            if voisin not in visites:
                if dfs(voisin, sommet):
                    return True
            elif voisin != parent:
                return True  # arête de retour → cycle
        return False

    for s in graphe:
        if s not in visites:
            if dfs(s, -1):
                return True
    return False
```

### Dans un graphe orienté (coloration)

```python
def a_cycle_oriente(graphe):
    # 0 = non visité, 1 = en cours, 2 = terminé
    couleur = {s: 0 for s in graphe}

    def dfs(s):
        couleur[s] = 1
        for voisin in graphe.get(s, []):
            if couleur[voisin] == 1:
                return True  # arête vers sommet en cours → cycle
            if couleur[voisin] == 0 and dfs(voisin):
                return True
        couleur[s] = 2
        return False

    return any(dfs(s) for s in graphe if couleur[s] == 0)
```

## Comparaison des algorithmes

| Algorithme | Usage | Complexité | Poids négatifs |
|---|---|---|---|
| BFS | Plus court chemin (non pondéré) | O(V+E) | N/A |
| DFS | Exploration, cycles, topo | O(V+E) | N/A |
| Dijkstra | Plus court chemin source unique | O((V+E) log V) | Non |
| Bellman-Ford | Plus court chemin, poids négatifs | O(VE) | Oui |
| Floyd-Warshall | Toutes les paires | O(V³) | Oui |
| Prim | MST | O(E log V) | N/A |
| Kruskal | MST | O(E log E) | N/A |
