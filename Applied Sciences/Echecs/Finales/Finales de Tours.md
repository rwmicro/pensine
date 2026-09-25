---
title: "Finales de Tours"
domain: "Applied Sciences"
subdomain: "Echecs > Finales"
tags: [sciences-appliquées, échecs]
date: "2026-03-20"
---

# Finales de Tours

Les finales de tours sont les plus fréquentes en pratique. Deux positions théoriques sont incontournables : **Lucena**, que le camp fort gagne, et **Philidor**, que le camp faible annule. Presque toutes les finales tour et pion contre tour se ramènent à l'une ou à l'autre.

## Position de Lucena (gain)

Le camp fort a un pion en 7e rangée, son roi est sur la case de promotion, et le roi adverse est coupé d'au moins une colonne par la tour. La seule difficulté est de sortir le roi de devant son pion sans subir des échecs sans fin sur les côtés.

**Méthode du pont**
1. Chasser d'abord le roi adverse d'une colonne de plus, par un échec.
2. Placer la tour sur la **4e rangée**.
3. Sortir le roi. Quand les échecs verticaux s'épuisent, la tour s'interpose en 4e rangée : c'est le « pont ».

```widget:echiquier
fen: 3K4/3P1k2/8/8/8/8/2r5/4R3 w - - 0 1
moves: e1f1 f7g7 f1f4 c2c1 d8e7 c1e1 e7d6 e1d1 d6e6 d1e1 e6d5 e1d1 f4d4
```

1.Tf1+ Rg7 2.Tf4! Tc1 3.Re7 Te1+ 4.Rd6 Td1+ 5.Re6 Te1+ 6.Rd5 Td1+ 7.Td4, et plus rien n'empêche le pion d'aller à dame.

> [!important] Idée clé
> Lucena fonctionne parce que le pont transforme les échecs latéraux, qui empêcheraient normalement la promotion, en une simple interposition. La tour se glisse entre le roi et la tour adverse sans pouvoir être prise. C'est un des rares cas où la tour protège activement le roi au lieu de l'inverse.

## Position de Philidor (nulle)

Le camp faible défend avec roi et tour contre roi, tour et pion. Son roi est sur la case de promotion ou juste à côté, et le pion n'a pas encore atteint la 6e rangée.

**Méthode de Philidor (1777)**
1. Tant que le pion n'a pas avancé, la tour reste sur la **6e rangée** (vue du camp attaquant). Elle interdit au roi adverse d'y entrer, donc de s'abriter devant son pion.
2. Dès que le pion avance en 6e, le roi attaquant n'a plus d'abri devant lui. La tour descend alors tout au fond et donne des échecs **par derrière**.
3. Le roi attaquant ne peut pas échapper à ces échecs sans abandonner son pion : c'est nulle.

```widget:echiquier
fen: 4k3/1R6/r7/4PK2/8/8/8/8 w - - 0 1
moves: e5e6 a6a1 f5f6 a1f1 f6e5 f1e1 e5d6 e1d1
```

1.e6 Ta1! 2.Rf6 Tf1+ 3.Re5 Te1+ 4.Rd6 Td1+, et les échecs continuent.

> [!warning] Piège
> L'erreur classique du camp faible est de garder sa tour passive sur sa dernière rangée. Le roi attaquant entre alors en 6e rangée, le pion le suit, et les échecs par derrière arrivent trop tard : le roi a un abri. Toute la défense tient au fait d'interdire la 6e rangée **avant** que le pion n'y arrive.

## Coupure du roi

La **coupure verticale** place la tour sur une colonne pour empêcher le roi adverse de rejoindre le pion. Plus le roi est coupé de colonnes, plus le gain est facile : à partir de deux colonnes, la plupart des positions gagnent.

La **coupure horizontale** confine le roi adverse sur quelques rangées, par exemple quand il se trouve loin derrière le pion.

## Principes généraux des finales de tours

| Principe | Explication |
|---|---|
| Tour active | Une tour qui attaque ou donne des échecs vaut plus qu'une tour qui défend. Mieux vaut souvent rendre un pion que laisser sa tour devenir passive |
| Tour derrière le pion passé | Qu'il soit ami ou ennemi : c'est la règle de Tarrasch |
| 7e rangée | Une tour sur la 7e rangée attaque les pions restés sur leur case de départ et enferme le roi |
| Roi actif | En finale de tours, le roi devient une pièce combattante |
| Deux tours sur la 7e | Presque toujours décisif |

> [!tip] Méthode
> La règle de Tarrasch surprend parce qu'elle vaut dans les deux sens. Derrière **son** pion passé, la tour le pousse en le protégeant tout au long de sa marche, et sa portée augmente à chaque pas. Derrière le pion passé **adverse**, elle l'attaque sans gêner son propre roi, et chaque case gagnée par le pion lui ouvre plus de colonne. La position de Philidor n'y contredit pas : les échecs par derrière, c'est déjà la tour derrière le pion.

## Tour et pions contre tour

Avec **un pion de plus**, la finale est souvent gagnante sur l'échiquier, mais beaucoup de ces positions sont en réalité nulles avec une défense précise. D'où l'adage : « toutes les finales de tours sont nulles ». Le pion de tour (a ou h) est le moins dangereux, parce que son roi a du mal à sortir de devant lui.

Avec **deux pions de plus**, le gain est presque toujours au rendez-vous. On crée un pion passé ou on force la tour adverse à se sacrifier pour lui.

## Positions théoriques à connaître

- **Lucena** : gain, pion en 7e, roi sur la case de promotion, roi adverse coupé.
- **Philidor** : nulle, tour sur la 6e rangée, puis échecs par derrière.
- **Pion de tour** : souvent nulle, même avec un pion de plus, si le roi défenseur atteint le coin ou si sa tour attaque le pion par le côté.
