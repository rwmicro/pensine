---
title: "Règles et Bases"
domain: "Applied Sciences"
subdomain: "Echecs"
tags: [sciences-appliquées, échecs]
date: "2026-02-22"
---
# Règles et Bases


### Plateau et Pièces

**Échiquier**
- 8×8 = 64 cases, alternance blanc-noir
- Coordonnées : colonnes (a-h), rangées (1-8)
- h1 = case blanche coin droit joueur blanc

**Pièces (par joueur)**
- **Roi** (♔ ♚) : 1
- **Dame** (♕ ♛) : 1
- **Tours** (♖ ♜) : 2
- **Fous** (♗ ♝) : 2
- **Cavaliers** (♘ ♞) : 2
- **Pions** (♙ ♟) : 8

**Valeur Relative**
- Pion = 1 point
- Cavalier = 3
- Fou = 3 (légèrement supérieur en finale ouverte)
- Tour = 5
- Dame = 9
- Roi = infini (objectif du jeu)

### Mouvements des Pièces

**Roi**
- 1 case dans toutes directions (horizontal, vertical, diagonal)
- **Roque** : mouvement spécial (une fois/partie, conditions strictes)
  - Petit roque (0-0) : Roi e1→g1, Tour h1→f1
  - Grand roque (0-0-0) : Roi e1→c1, Tour a1→d1
  - Conditions : Roi et Tour pas bougés, cases vides, Roi pas en échec

**Dame**
- Illimité horizontal, vertical, diagonal
- Pièce la plus puissante

**Tour**
- Illimité horizontal, vertical

**Fou**
- Illimité diagonal
- Cases de même couleur uniquement (clair ou foncé)

**Cavalier**
- En "L" : 2 cases + 1 perpendiculaire
- Seule pièce pouvant sauter par-dessus autres

**Pion**
- 1 case avant (2 cases si position initiale)
- Capture diagonale
- **Promotion** : atteint 8e rangée → Dame/Tour/Fou/Cavalier
- **Prise en passant** : capture pion adverse ayant avancé 2 cases

### Objectif et Fin de Partie

**Échec et Mat**
- Roi attaqué (échec) sans possibilité d'échapper
- Joueur mis en échec et mat perd

**Pat**
- Joueur au trait n'a aucun coup légal mais n'est pas en échec
- Nulle

**Autres Nulles**
- Matériel insuffisant (Roi seul vs Roi seul, etc.)
- Triple répétition position
- Règle des 50 coups (sans capture ni mouvement pion)
- Accord mutuel

