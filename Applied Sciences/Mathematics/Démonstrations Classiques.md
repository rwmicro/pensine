---
title: "Démonstrations Classiques"
domain: "Applied Sciences"
subdomain: "Mathematics"
tags: [sciences-appliquées, mathématiques, démonstrations, preuves, classiques]
date: "2026-05-20"
---

# Démonstrations Classiques

Certaines preuves traversent les siècles non pas par utilité, mais par **élégance**. Elles sont des modèles de raisonnement et fonctionnent comme des étalons : si tu les connais, tu reconnais leur structure dans des dizaines d'autres preuves. Cette note rassemble les démonstrations canoniques que tout étudiant en mathématiques devrait avoir vues.

## 1. Irrationalité de $\sqrt{2}$

**Origine** : pythagoriciens (Ve s. av. J.-C.) — légende rapportée par Pappus : Hippase, qui aurait divulgué la découverte, aurait été noyé en représailles.

**Méthode** : par l'absurde + descente infinie.

> [!example] $\sqrt{2} \notin \mathbb{Q}$
> Supposons $\sqrt{2} = p/q$ avec $p, q \in \mathbb{Z}$, $q > 0$, $\gcd(p, q) = 1$.
>
> Alors $2 q^2 = p^2$, donc $p^2$ est pair. Or si $p$ est impair, $p^2$ l'est aussi. Donc $p$ est pair : écrivons $p = 2k$.
>
> Substituant : $2q^2 = 4k^2$, donc $q^2 = 2k^2$. Par le même argument, $q$ est pair.
>
> Mais $p$ et $q$ tous les deux pairs contredit $\gcd(p, q) = 1$. CQFD.

**Importance** : premier exemple historique d'une grandeur incommensurable — choc philosophique chez les pythagoriciens, qui pensaient que tout est nombre (entier ou rationnel).

## 2. Infinité des nombres premiers (Euclide, Éléments IX-20)

**Méthode** : par l'absurde.

> [!example] Il existe une infinité de nombres premiers
> Supposons que les nombres premiers soient en nombre fini : $p_1 < p_2 < \cdots < p_n$.
>
> Posons $N = p_1 p_2 \cdots p_n + 1$. Alors $N \geq 2$, donc $N$ admet au moins un diviseur premier $p$.
>
> Si $p = p_i$ pour un $i$, alors $p \mid p_1 \cdots p_n$. Combiné à $p \mid N$, cela donne $p \mid (N - p_1 \cdots p_n) = 1$ — absurde.
>
> Donc $p$ n'est aucun des $p_i$, ce qui contredit la finitude supposée.

**Importance** : démonstration de pure beauté, 5 lignes pour un résultat fondamental. Modèle de raisonnement par l'absurde.

## 3. Théorème de Pythagore — preuve par découpage

**Origine** : connu de plusieurs civilisations (babylonienne, chinoise, indienne) avant Pythagore. Plus de 350 preuves connues.

> [!example] Dans un triangle rectangle d'hypoténuse $c$ et de cathètes $a, b$ : $a^2 + b^2 = c^2$
>
> **Preuve par découpage chinois (Zhou Bi Suan Jing, ~Ier s.)** :
>
> On dispose 4 triangles rectangles identiques dans un carré de côté $a+b$, de deux façons :
>
> - Configuration 1 : les triangles laissent au milieu **deux carrés**, de côtés $a$ et $b$. Aire centrale : $a^2 + b^2$.
> - Configuration 2 : les triangles laissent au milieu **un seul carré** de côté $c$. Aire centrale : $c^2$.
>
> Comme l'aire totale est la même ($(a+b)^2$) et les 4 triangles aussi ($2ab$), on a $a^2 + b^2 = c^2$.

**Importance** : exemple-clé du **raisonnement visuel** en géométrie. La preuve d'Euclide (Éléments I-47) est différente, plus algébrique.

## 4. Somme des $n$ premiers entiers : $\sum_{k=1}^n k = \frac{n(n+1)}{2}$

**Origine** : anecdote du jeune Gauss à 7 ans à qui le maître ordonne d'additionner les nombres de 1 à 100 — Gauss donne instantanément 5 050.

> [!example] Preuve sans récurrence (méthode de Gauss)
> Écrivons la somme dans les deux sens :
> $$S = 1 + 2 + 3 + \cdots + (n-1) + n$$
> $$S = n + (n-1) + (n-2) + \cdots + 2 + 1$$
>
> En additionnant terme à terme : chaque colonne fait $n+1$, et il y a $n$ colonnes.
> $$2S = n(n+1) \quad \Rightarrow \quad S = \frac{n(n+1)}{2}$$

**Importance** : montre qu'une preuve directe peut être plus élégante qu'une récurrence.

## 5. La somme des inverses des carrés (problème de Bâle, Euler 1735)

**Énoncé** : Pour quelle valeur $L$ a-t-on $\sum_{n=1}^{\infty} \frac{1}{n^2} = L$ ?

Posé en 1644 par Pietro Mengoli, résolu en 1735 par **Euler** (28 ans), qui devient célèbre pour ce résultat.

> [!example] Esquisse de la preuve d'Euler
> Euler note que la fonction $\frac{\sin(\pi x)}{\pi x}$ a pour zéros $x = \pm 1, \pm 2, \pm 3, \dots$ et vaut $1$ en $0$.
>
> Il « factorise » comme un polynôme infini :
> $$\frac{\sin(\pi x)}{\pi x} = \prod_{n=1}^{\infty}\left(1 - \frac{x^2}{n^2}\right)$$
>
> Par développement en série, le coefficient de $x^2$ dans le membre de gauche est $-\pi^2/6$ (vient du DL de $\sin$).
>
> Dans le membre de droite, le coefficient de $x^2$ est $-\sum_{n=1}^\infty 1/n^2$.
>
> Par identification : $\sum_{n=1}^\infty \frac{1}{n^2} = \frac{\pi^2}{6}$.

**Importance** : ouvre la voie à la théorie des fonctions zêta. Démonstration formellement non rigoureuse (par les standards modernes) mais profonde. Plusieurs preuves rigoureuses existent aujourd'hui.

## 6. Identité d'Euler : $e^{i\pi} + 1 = 0$

> [!quote] Richard Feynman
> « La formule la plus remarquable de toutes les mathématiques. »

Relie cinq constantes fondamentales : $0, 1, e, i, \pi$, et trois opérations : addition, multiplication, exponentiation.

> [!example] Preuve
> Par définition de l'exponentielle complexe :
> $$e^{ix} = \cos x + i \sin x$$
> (Formule d'Euler générale, prouvée par les séries de Taylor.)
>
> En particulier pour $x = \pi$ :
> $$e^{i\pi} = \cos \pi + i \sin \pi = -1 + 0 \cdot i = -1$$
> Donc $e^{i\pi} + 1 = 0$.

**Importance** : l'identité résume l'unité profonde de l'analyse, de la trigonométrie et de l'algèbre.

## 7. Cantor — $\mathbb{R}$ n'est pas dénombrable (argument diagonal, 1891)

> [!example] L'argument diagonal de Cantor
> Supposons par l'absurde que $[0, 1]$ soit dénombrable. On peut donc lister tous ses éléments :
> $$x_1 = 0{,}a_{1,1} a_{1,2} a_{1,3} a_{1,4} \dots$$
> $$x_2 = 0{,}a_{2,1} a_{2,2} a_{2,3} a_{2,4} \dots$$
> $$x_3 = 0{,}a_{3,1} a_{3,2} a_{3,3} a_{3,4} \dots$$
> $$\vdots$$
>
> Construisons $y = 0{,}b_1 b_2 b_3 b_4 \dots$ où $b_n \neq a_{n,n}$ (par exemple, $b_n = 5$ si $a_{n,n} \neq 5$, sinon $b_n = 6$).
>
> Alors $y \in [0, 1]$ mais $y \neq x_n$ pour tout $n$ (ils diffèrent en position $n$). Contradiction avec l'exhaustivité de la liste.

**Importance** : ouvre la théorie des **infinis de cardinaux différents**. $|\mathbb{N}| < |\mathbb{R}|$ ; les rationnels sont dénombrables, les réels non. Choc philosophique au XIXe siècle.

## 8. Le paradoxe de Banach-Tarski (1924)

**Énoncé** : on peut découper une boule en un nombre fini de morceaux et les réassembler (par rotations et translations) en deux boules de même volume que l'originale.

Conséquence de l'**axiome du choix** appliqué à des ensembles non mesurables. Démonstration techniquement avancée, mais énoncé qui défie toute intuition.

**Importance** : illustre les limites de notre intuition géométrique et le rôle subtil de l'axiome du choix.

## 9. Théorème fondamental de l'algèbre (Gauss, 1799)

**Énoncé** : tout polynôme non constant à coefficients complexes admet au moins une racine complexe.

**Méthode classique** : par l'absurde, en utilisant l'analyse complexe (théorème de Liouville).

> [!example] Esquisse
> Soit $P(z) = a_n z^n + \cdots + a_0$ non constant. Supposons que $P$ n'admette aucune racine. Alors $1/P$ est entière (holomorphe sur $\mathbb{C}$).
>
> Pour $|z|$ grand, $|P(z)| \to \infty$ (terme dominant), donc $1/P \to 0$. En particulier $1/P$ est bornée.
>
> Par le théorème de Liouville, toute fonction entière bornée est constante. Donc $P$ est constante — contradiction.

**Importance** : explique pourquoi $\mathbb{C}$ est « algébriquement clos », ce que $\mathbb{R}$ n'est pas ($x^2 + 1$ n'a pas de racine réelle).

## 10. Théorème de Pythagore appliqué — non-cubabilité de la sphère

Plus généralement, beaucoup de **résultats d'impossibilité** célèbres :
- **Quadrature du cercle** impossible à la règle et au compas (Lindemann, 1882 : $\pi$ transcendant)
- **Trisection de l'angle** impossible en général (Wantzel, 1837)
- **Duplication du cube** impossible (Wantzel, 1837)
- Les **équations polynomiales de degré $\geq 5$** n'ont pas de formule par radicaux (Abel-Ruffini, 1824 ; Galois)

Tous démontrés par des méthodes algébriques abstraites — théorie de Galois, transcendance.

## 11. Théorème des valeurs intermédiaires (TVI)

**Énoncé** : Si $f$ est continue sur $[a, b]$ et $f(a) \cdot f(b) < 0$, alors $f$ s'annule sur $]a, b[$.

> [!example] Preuve par dichotomie
> Sans perte de généralité $f(a) < 0 < f(b)$. Posons $a_0 = a,\; b_0 = b$.
>
> À chaque étape, on regarde $m_n = (a_n + b_n)/2$ :
> - si $f(m_n) > 0$, on pose $a_{n+1} = a_n,\; b_{n+1} = m_n$
> - si $f(m_n) < 0$, on pose $a_{n+1} = m_n,\; b_{n+1} = b_n$
> - si $f(m_n) = 0$, on a fini
>
> Les suites $(a_n)$ et $(b_n)$ sont adjacentes (la première croît, la seconde décroît, $b_n - a_n \to 0$). Elles convergent vers une limite commune $c$. Par continuité, $f(c) = \lim f(a_n) \leq 0$ et $f(c) = \lim f(b_n) \geq 0$, donc $f(c) = 0$.

**Importance** : illustre le pouvoir de la **complétude** de $\mathbb{R}$. Sans complétude (sur $\mathbb{Q}$), le TVI est faux ($x^2 - 2$ change de signe sans s'annuler dans $\mathbb{Q}$).

## 12. Lemme de Bézout

**Énoncé** : $\gcd(a, b) = d$ ssi il existe $u, v \in \mathbb{Z}$ tels que $au + bv = d$.

**Preuve constructive** par algorithme d'Euclide étendu — qu'on peut tracer en quelques lignes.

**Importance** : pierre angulaire de l'arithmétique. Permet de prouver le théorème de Gauss, l'unicité de la décomposition en premiers, et de construire concrètement les inverses modulaires (utilisés en RSA).

## 13. Théorème d'Euler pour les polyèdres

**Énoncé** : Pour tout polyèdre convexe, $V - E + F = 2$ (sommets - arêtes + faces).

| Polyèdre | V | E | F | V-E+F |
|---|---|---|---|---|
| Tétraèdre | 4 | 6 | 4 | 2 |
| Cube | 8 | 12 | 6 | 2 |
| Octaèdre | 6 | 12 | 8 | 2 |
| Dodécaèdre | 20 | 30 | 12 | 2 |
| Icosaèdre | 12 | 30 | 20 | 2 |

**Importance** : premier invariant **topologique** identifié — annonce la naissance de la topologie. Généralisable aux surfaces : $V - E + F = 2 - 2g$ où $g$ est le « genre » (nombre de trous).

## Pourquoi connaître ces démonstrations

Au-delà des théorèmes eux-mêmes, ces preuves sont des **patrons** :
- L'argument diagonal de Cantor sert dans la démonstration de l'indécidabilité (Gödel, Turing).
- La preuve d'Euclide sur les premiers sert de modèle pour montrer qu'une famille est infinie.
- Le découpage de Pythagore est l'archétype de la preuve géométrique visuelle.
- L'analyse-synthèse pair/impair se rencontre dans toute décomposition canonique.

Maîtriser ces classiques, c'est se constituer une **bibliothèque mentale** d'astuces réutilisables.
