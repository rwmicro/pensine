---
title: "Géométrie — Formules et Exercices corrigés"
domain: "Applied Sciences"
subdomain: "Mathematics > Lycée > Géométrie"
tags: [sciences-appliquées, mathématiques]
date: "2026-02-22"
---

# Géométrie — Formules et Exercices corrigés

Ce fichier rassemble les formules essentielles et les exercices types pour la géométrie lycée (plane et dans l'espace).


## 13. Résumé des formules essentielles

> [!tip] Aide-mémoire
>
> **Dans le plan (repère orthonormé) :**
> | Concept | Formule |
> |---|---|
> | Distance $AB$ | $\sqrt{(x_B-x_A)^2+(y_B-y_A)^2}$ |
> | Milieu | $\left(\frac{x_A+x_B}{2}, \frac{y_A+y_B}{2}\right)$ |
> | Colinéarité | $xy'-x'y = 0$ |
> | Produit scalaire | $xx'+yy'$ |
> | Orthogonalité | $\vec{u}\cdot\vec{v}=0$ |
> | Parallélisme | $m_1 = m_2$ ou $a_1b_2=a_2b_1$ |
> | Perpendicularité | $m_1 m_2 = -1$ ou $a_1a_2+b_1b_2=0$ |
>
> **Dans l'espace (repère orthonormé) :**
> | Concept | Formule |
> |---|---|
> | Distance $AB$ | $\sqrt{(x_B-x_A)^2+(y_B-y_A)^2+(z_B-z_A)^2}$ |
> | Produit scalaire | $xx'+yy'+zz'$ |
> | Distance point-plan | $\frac{\|ax_0+by_0+cz_0+d\|}{\sqrt{a^2+b^2+c^2}}$ |
> | Droite $\perp$ plan | vecteur directeur = vecteur normal |


## 14. Exercices types corrigés

### Exercice 1 : Équation de droite et intersection

> [!example] Énoncé
> Soient les droites $(d_1) : 2x - y + 3 = 0$ et $(d_2) : x + 3y - 7 = 0$.
> Déterminer leur point d'intersection.

**Solution :**

On résout le système :
$$\begin{cases} 2x - y = -3 \\ x + 3y = 7 \end{cases}$$

De la première : $y = 2x + 3$.
On substitue dans la deuxième : $x + 3(2x+3) = 7 \implies x + 6x + 9 = 7 \implies 7x = -2 \implies x = -\frac{2}{7}$

$y = 2 \times \left(-\frac{2}{7}\right) + 3 = -\frac{4}{7} + \frac{21}{7} = \frac{17}{7}$

$$\boxed{I\left(-\frac{2}{7}\;;\;\frac{17}{7}\right)}$$


### Exercice 2 : Produit scalaire et angle

> [!example] Énoncé
> Dans un repère orthonormé, on donne $A(1,3)$, $B(4,1)$, $C(2,6)$.
> Calculer l'angle $\widehat{BAC}$.

**Solution :**

$\overrightarrow{AB} = (3, -2)$ et $\overrightarrow{AC} = (1, 3)$

$\overrightarrow{AB} \cdot \overrightarrow{AC} = 3 \times 1 + (-2) \times 3 = 3 - 6 = -3$

$\|\overrightarrow{AB}\| = \sqrt{9+4} = \sqrt{13}$

$\|\overrightarrow{AC}\| = \sqrt{1+9} = \sqrt{10}$

$\cos(\widehat{BAC}) = \frac{-3}{\sqrt{13}\times\sqrt{10}} = \frac{-3}{\sqrt{130}}$

$$\boxed{\widehat{BAC} = \arccos\left(\frac{-3}{\sqrt{130}}\right) \approx 105{,}3°}$$


### Exercice 3 : Équation de plan

> [!example] Énoncé
> Déterminer l'équation cartésienne du plan passant par $A(1, 0, 2)$, $B(3, 1, -1)$, $C(0, 2, 1)$.

**Solution :**

*Étape 1 :* Calculer deux vecteurs du plan.
$\overrightarrow{AB} = (2, 1, -3)$ et $\overrightarrow{AC} = (-1, 2, -1)$

*Étape 2 :* Trouver un vecteur normal $\vec{n}(a, b, c)$ orthogonal aux deux.
$$\begin{cases} \vec{n} \cdot \overrightarrow{AB} = 0 : & 2a + b - 3c = 0 \\ \vec{n} \cdot \overrightarrow{AC} = 0 : & -a + 2b - c = 0 \end{cases}$$

De la deuxième : $a = 2b - c$. On substitue dans la première :
$2(2b-c) + b - 3c = 0 \implies 5b - 5c = 0 \implies b = c$

On choisit $b = c = 1$, d'où $a = 2(1) - 1 = 1$.

Donc $\vec{n} = (1, 1, 1)$.

*Étape 3 :* Écrire l'équation avec le point $A(1,0,2)$ :
$1(x-1) + 1(y-0) + 1(z-2) = 0$

$$\boxed{x + y + z - 3 = 0}$$

*Vérification :* $A : 1+0+2-3 = 0$ ; $B : 3+1-1-3 = 0$ ; $C : 0+2+1-3 = 0$. Correct.


### Exercice 4 : Position relative dans l'espace

> [!example] Énoncé
> Étudier la position relative de la droite $(d)$ de représentation paramétrique $\begin{cases} x = 1 + 2t \\ y = -1 + t \\ z = 3 - t \end{cases}$ et du plan $(\mathcal{P}) : x + y + z - 5 = 0$.

**Solution :**

Le vecteur directeur de $(d)$ est $\vec{u} = (2, 1, -1)$.
Le vecteur normal de $(\mathcal{P})$ est $\vec{n} = (1, 1, 1)$.

$\vec{u} \cdot \vec{n} = 2 + 1 - 1 = 2 \neq 0$

Donc la droite et le plan sont **sécants**.

*Point d'intersection :* On substitue les expressions paramétriques dans l'équation du plan :
$(1+2t) + (-1+t) + (3-t) - 5 = 0$
$1 + 2t - 1 + t + 3 - t - 5 = 0$
$2t - 2 = 0$
$t = 1$

Point d'intersection : $(x, y, z) = (3, 0, 2)$.

$$\boxed{(d) \text{ et } (\mathcal{P}) \text{ sont sécants en } I(3, 0, 2)}$$


### Exercice 5 : Distance point-plan

> [!example] Énoncé
> Calculer la distance du point $M(3, -1, 2)$ au plan $(\mathcal{P}) : 3x - 4y + 12z + 1 = 0$.

**Solution :**

$$d(M, \mathcal{P}) = \frac{|3(3) - 4(-1) + 12(2) + 1|}{\sqrt{9 + 16 + 144}} = \frac{|9 + 4 + 24 + 1|}{\sqrt{169}} = \frac{38}{13}$$

$$\boxed{d(M, \mathcal{P}) = \frac{38}{13} \approx 2{,}92}$$


### Exercice 6 : Projeté orthogonal et distance à une droite

> [!example] Énoncé
> Soit la droite $(d)$ passant par $A(1, 1, 0)$ de vecteur directeur $\vec{u}(1, -1, 1)$ et le point $M(3, 2, 1)$.
> Calculer le projeté orthogonal $H$ de $M$ sur $(d)$ et la distance $d(M, d)$.

**Solution :**

$\overrightarrow{AM} = (2, 1, 1)$

$t = \frac{\overrightarrow{AM} \cdot \vec{u}}{\|\vec{u}\|^2} = \frac{2(-1)(1) + 1(-1) + 1(1)}{1+1+1}$

Corrigeons : $\overrightarrow{AM} \cdot \vec{u} = 2 \times 1 + 1 \times (-1) + 1 \times 1 = 2 - 1 + 1 = 2$

$\|\vec{u}\|^2 = 1 + 1 + 1 = 3$

$t = \frac{2}{3}$

$H = A + \frac{2}{3}\vec{u} = \left(1 + \frac{2}{3},\; 1 - \frac{2}{3},\; 0 + \frac{2}{3}\right) = \left(\frac{5}{3},\; \frac{1}{3},\; \frac{2}{3}\right)$

$\overrightarrow{MH} = \left(\frac{5}{3}-3,\; \frac{1}{3}-2,\; \frac{2}{3}-1\right) = \left(-\frac{4}{3},\; -\frac{5}{3},\; -\frac{1}{3}\right)$

$d(M, d) = \|\overrightarrow{MH}\| = \sqrt{\frac{16}{9}+\frac{25}{9}+\frac{1}{9}} = \sqrt{\frac{42}{9}} = \frac{\sqrt{42}}{3}$

$$\boxed{H = \left(\frac{5}{3},\; \frac{1}{3},\; \frac{2}{3}\right), \quad d(M, d) = \frac{\sqrt{42}}{3} \approx 2{,}16}$$


## Liens

- [[Index]] — vue d'ensemble du dossier Mathématiques
- [[Géométrie Plane]] — théorie de la géométrie plane au Lycée
- [[Géométrie dans l'Espace]] — extension en dimension 3
- [[Trigonométrie]] — formules trigonométriques associées
- [[Nombres Complexes]] — interprétation géométrique des complexes
- [[Formulaire]] — toutes les formules mathématiques en un coup d'œil