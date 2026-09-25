---
title: "Règles et Bases"
domain: "Applied Sciences"
subdomain: "Echecs"
tags: [sciences-appliquées, échecs]
date: "2026-02-22"
---
# Règles et Bases

Les échecs se jouent à deux, sur un plateau de 64 cases, avec seize pièces chacun. Le but est de mettre le roi adverse échec et mat.

## Plateau et pièces

**L'échiquier** compte 8 × 8 = 64 cases, alternativement claires et foncées. Les colonnes sont nommées de a à h, les rangées de 1 à 8, depuis le côté des Blancs. On le pose de sorte que chaque joueur ait une case claire dans son coin droit (h1 pour les Blancs).

**Les pièces.** Chaque joueur a un roi, une dame, deux tours, deux fous, deux cavaliers et huit pions.

| Pièce | Symboles | Notation | Nombre | Valeur relative |
|---|---|---|---|---|
| Roi | ♔ ♚ | R | 1 | Infinie (sa perte termine la partie) |
| Dame | ♕ ♛ | D | 1 | 9 |
| Tour | ♖ ♜ | T | 2 | 5 |
| Fou | ♗ ♝ | F | 2 | 3 |
| Cavalier | ♘ ♞ | C | 2 | 3 |
| Pion | ♙ ♟ | (aucune lettre) | 8 | 1 |

> [!warning] Piège
> Ces valeurs sont des repères moyens, pas des constantes physiques. Un fou vaut nettement plus qu'un cavalier en finale ouverte avec des pions sur les deux ailes, et l'inverse dans une position fermée et verrouillée. Compter mécaniquement les points sans regarder la structure de pions est l'erreur la plus commune des débutants pour juger un échange.

## Le déplacement des pièces

**Le roi** avance d'une case dans n'importe quelle direction. Il ne peut jamais se placer sur une case attaquée.

**Le roque** est le seul coup où deux pièces bougent à la fois : le roi se déplace de deux cases vers une tour, et la tour passe par-dessus lui.
- Petit roque (0-0) : roi e1 → g1, tour h1 → f1.
- Grand roque (0-0-0) : roi e1 → c1, tour a1 → d1.

Le roque n'est permis que si :
1. ni le roi ni cette tour n'ont encore bougé ;
2. les cases entre le roi et la tour sont vides ;
3. le roi n'est pas en échec ;
4. le roi ne traverse aucune case attaquée ;
5. le roi n'arrive pas sur une case attaquée.

**La dame** se déplace d'autant de cases qu'elle veut, en ligne droite ou en diagonale. C'est la pièce la plus puissante.

**La tour** se déplace d'autant de cases qu'elle veut, sur sa rangée ou sa colonne.

**Le fou** se déplace d'autant de cases qu'il veut, en diagonale. Il reste donc toute la partie sur des cases de la même couleur.

**Le cavalier** se déplace en « L » : deux cases dans une direction, puis une case perpendiculairement. C'est la seule pièce qui saute par-dessus les autres.

**Le pion** avance d'une case droit devant lui, ou de deux cases depuis sa case de départ. Il prend en diagonale, d'une case vers l'avant. Deux règles spéciales s'y ajoutent :
- la **promotion** : un pion qui atteint la dernière rangée est remplacé, au choix, par une dame, une tour, un fou ou un cavalier ;
- la **prise en passant** : un pion qui avance de deux cases et s'arrête à côté d'un pion adverse peut être pris par celui-ci comme s'il n'avait avancé que d'une case.

> [!warning] Piège
> Le droit de prise en passant n'existe qu'au coup immédiatement suivant l'avance de deux cases. Un coup plus tard, il est perdu définitivement, même si la position semble identique. Beaucoup de joueurs découvrent cette règle en la ratant, jamais en la sur-utilisant.

## Fin de partie

**L'échec et mat.** Le roi est attaqué (il est en échec) et aucun coup ne peut parer l'attaque. Le joueur maté perd la partie.

**Le pat.** Le joueur au trait n'a aucun coup légal, mais son roi n'est pas en échec. La partie est nulle.

> [!important] Idée clé
> Le pat n'est pas qu'une curiosité de règlement : c'est la principale ressource de sauvetage du camp en infériorité matérielle. Voir [[Finales de Pions#L'exception du pion de tour (pion a ou h)|le pion de tour coincé dans le coin]] : le camp faible cherche activement le pat plutôt que de subir passivement la défaite.

**Les autres nulles.**
- **Matériel insuffisant** : aucun des deux camps ne peut mater, par exemple roi contre roi, ou roi et fou contre roi.
- **Triple répétition** : la même position se présente trois fois, avec le même joueur au trait.
- **Règle des 50 coups** : 50 coups de chaque camp se sont joués sans capture ni mouvement de pion.
- **Accord mutuel** entre les joueurs.
