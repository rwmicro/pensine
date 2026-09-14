---
title: "Finales de Tours"
domain: "Applied Sciences"
subdomain: "Echecs > Finales"
tags: [sciences-appliquées, échecs]
date: "2026-03-20"
---

# Finales de Tours

Les finales de tours sont les plus fréquentes en pratique. Deux positions théoriques sont incontournables : **Lucena** (gain) et **Philidor** (nulle).

### Position de Lucena (Gain)

Situation : le camp fort possède un pion passé presque promu, son roi est devant le pion, le roi adverse est coupé.

**Méthode du pont (building a bridge)**
1. Avancer la tour pour couper le roi adverse (colonne ou rangée)
2. Amener son roi se couvrir des échecs
3. Construire un « pont » avec la tour pour abriter le roi des échecs latéraux

```
Exemple schématique (Blancs gagnent) :
  Roi blanc : e7  Tour blanche : a1  Pion : e6
  Roi noir : g7   Tour noire : e8
  1. Ta7+ Rf8  2. Tf7+ Re8  3. Txe7+ Rd8  4. Tf7 ... (le pont est construit)
```

**Principe clé** : la tour se place sur la 4e rangée (ou 5e) pour écarter le roi ennemi des échecs perpétuels.

> [!important] Idée clé
> Lucena fonctionne parce que le "pont" transforme un échec latéral (qui empêcherait normalement la promotion) en une interposition : la tour se glisse entre le roi et la ligne d'échec, tout en restant assez loin pour ne pas être capturée au coup suivant. C'est un des rares cas en finale où la tour protège activement le roi au lieu de l'inverse.

### Position de Philidor (Nulle)

Situation : le camp faible défend avec roi et tour contre roi, tour et pion.

**Méthode de Philidor (1777)**
1. Placer la tour sur la 6e rangée (entre le pion et le roi adverse) — **la clé**
2. Quand le pion avance, passer la tour à la rangée de départ du pion pour donner des échecs par derrière
3. Les échecs perpétuels par derrière assurent la nulle

```
Exemple :
  Roi blanc : e5  Tour blanche : e1  Pion : e4
  Roi noir : e7   Tour noire : f6    ← Tour sur la 6e rangée
```

**À ne pas faire** : placer la tour derrière le pion adverse — le roi ennemi avance alors en bouclier.

> [!warning] Piège
> L'erreur classique du camp faible est de placer sa tour *devant* le pion adverse (sur son chemin) au lieu de sur la 6e rangée derrière la ligne d'échec. Cela semble bloquer le pion mais l'attaquant chasse la tour avec le pion lui-même, perdant le tempo qui aurait dû servir à donner des échecs.

### Coupure du Roi

**Coupure verticale** (colonnes) : empêcher le roi adverse de rejoindre le pion
- La tour coupe sur une colonne : le roi reste à distance horizontale imposée

**Coupure horizontale** (rangées) : confiner le roi adverse dans peu de rangées
- Plus la coupure est loin, meilleure elle est pour le camp fort

### Principes Généraux des Finales de Tours

| Principe | Explication |
|---|---|
| Tour active | La tour doit contrôler maximum de cases, ne pas être passive |
| Tour derrière le pion passé | Qu'il soit ami ou ennemi — principe de Nimzowitsch |

> [!tip] Méthode
> Ce principe surprend car il vaut dans les deux sens : derrière SON pion passé, la tour le pousse en le protégeant tout le long de sa marche ; derrière le pion passé ADVERSE, elle le bloque et gagne en portée à mesure qu'il avance (chaque case gagnée par le pion ouvre plus de colonne à la tour derrière lui).
| 7e rangée | Tour sur la 7e rangée = très forte (attaque pions non avancés) |
| Roi actif | En finale de tours, le roi devient une pièce combattante |
| Deux tours sur 7e | Quasi toujours décisif |

### Tour + Pions vs Tour

**Avantage d'un pion** : généralement gagnant mais technique requise
- Exception : pion de tour (a ou h) → souvent nulle (Philidor s'applique mal)
- Pion central (d, e) : gain le plus fiable

**Avantage de deux pions** : presque toujours gagnant
- Créer un pion passé ou forcer la tour adverse à se sacrifier

### Positions Théoriques à Connaître

- **Lucena** : gain avec pion sur 7e rangée, roi devant
- **Philidor** : nulle défensive (tour 6e rangée)
- **Salvioli** : variante de coupure verticale
- **Pion de tour + mauvais roi** : nulle (Ré8 dans le coin)
