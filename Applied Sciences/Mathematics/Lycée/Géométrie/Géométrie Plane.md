---
title: "Géométrie Plane (Seconde – Première)"
domain: "Applied Sciences"
subdomain: "Mathematics > Lycée > Géométrie"
tags: [sciences-appliquées, mathématiques]
date: "2026-02-22"
---

# Géométrie Plane (Seconde – Première)

> [!tip] Fil conducteur
> La géométrie plane couvre les repères, les vecteurs, les équations de droites et le produit scalaire. Ces outils se généralisent ensuite à la troisième dimension en Terminale.


# Partie I : Géométrie plane

## 1. Repère du plan et coordonnées (Seconde)

### 1.1 Repère cartésien

> [!important] Définition : Repère du plan
> Un **repère** du plan est constitué d'un point $O$ (origine) et de deux vecteurs $\vec{i}$ et $\vec{j}$ non colinéaires.
> - Si $\vec{i}$ et $\vec{j}$ sont orthogonaux : repère **orthogonal**.
> - Si de plus $\|\vec{i}\| = \|\vec{j}\| = 1$ : repère **orthonormé** (ou orthonormal).
>
> On note le repère $(O, \vec{i}, \vec{j})$ ou $(O; \vec{i}, \vec{j})$.

Tout point $M$ du plan est repéré par ses **coordonnées** $(x, y)$ :

$$\overrightarrow{OM} = x\vec{i} + y\vec{j}$$

- $x$ est l'**abscisse** de $M$.
- $y$ est l'**ordonnée** de $M$.

### 1.2 Distance entre deux points

> [!important] Formule : Distance
> Dans un repère orthonormé, la distance entre $A(x_A, y_A)$ et $B(x_B, y_B)$ est :
> $$AB = \sqrt{(x_B - x_A)^2 + (y_B - y_A)^2}$$

### 1.3 Milieu d'un segment

> [!important] Formule : Milieu
> Le milieu $I$ du segment $[AB]$ a pour coordonnées :
> $$I\left(\frac{x_A + x_B}{2}\;;\;\frac{y_A + y_B}{2}\right)$$

> [!example] Exemple
> Soient $A(1, 3)$ et $B(5, 7)$.
>
> $AB = \sqrt{(5-1)^2 + (7-3)^2} = \sqrt{16+16} = \sqrt{32} = 4\sqrt{2}$
>
> Milieu $I = \left(\frac{1+5}{2}, \frac{3+7}{2}\right) = (3, 5)$


## 2. Vecteurs (Seconde)

### 2.1 Définition

> [!important] Définition : Vecteur
> Un **vecteur** $\vec{u}$ est caractérisé par :
> - une **direction** (la droite qui le porte)
> - un **sens** (l'une des deux orientations de cette droite)
> - une **norme** (sa longueur) $\|\vec{u}\|$
>
> Le vecteur $\overrightarrow{AB}$ a pour représentant tout bipoint $(C, D)$ tel que $ABDC$ soit un parallélogramme.

### 2.2 Coordonnées d'un vecteur

Si $A(x_A, y_A)$ et $B(x_B, y_B)$ :

$$\overrightarrow{AB} = \begin{pmatrix} x_B - x_A \\ y_B - y_A \end{pmatrix}$$

### 2.3 Opérations sur les vecteurs

**Addition :** Si $\vec{u} = \begin{pmatrix} x \\ y \end{pmatrix}$ et $\vec{v} = \begin{pmatrix} x' \\ y' \end{pmatrix}$ :

$$\vec{u} + \vec{v} = \begin{pmatrix} x + x' \\ y + y' \end{pmatrix}$$

**Multiplication par un scalaire :** Pour $k \in \mathbb{R}$ :

$$k\vec{u} = \begin{pmatrix} kx \\ ky \end{pmatrix}$$

**Relation de Chasles :** Pour tous points $A$, $B$, $C$ :

$$\overrightarrow{AC} = \overrightarrow{AB} + \overrightarrow{BC}$$

**Norme :** Dans un repère orthonormé :

$$\|\vec{u}\| = \sqrt{x^2 + y^2}$$

### 2.4 Colinéarité

> [!important] Définition : Colinéarité
> Deux vecteurs $\vec{u}(x, y)$ et $\vec{v}(x', y')$ sont **colinéaires** si et seulement si :
> $$xy' - x'y = 0$$
> Ce nombre $xy' - x'y$ est appelé le **déterminant** de $(\vec{u}, \vec{v})$.

> [!tip] Applications de la colinéarité
> - Trois points $A$, $B$, $C$ sont **alignés** $\iff$ $\overrightarrow{AB}$ et $\overrightarrow{AC}$ sont colinéaires.
> - Deux droites sont **parallèles** $\iff$ leurs vecteurs directeurs sont colinéaires.

> [!example] Exemple
> $A(1,2)$, $B(3,5)$, $C(7,11)$.
> $\overrightarrow{AB} = (2,3)$ et $\overrightarrow{AC} = (6,9)$.
> $\det(\overrightarrow{AB}, \overrightarrow{AC}) = 2 \times 9 - 3 \times 6 = 18 - 18 = 0$.
> Les vecteurs sont colinéaires, donc $A$, $B$, $C$ sont **alignés**.


## 3. Équations de droites (Seconde)

### 3.1 Équation réduite

> [!important] Définition : Équation réduite
> Toute droite non verticale du plan admet une équation de la forme :
> $$y = mx + p$$
> - $m$ est le **coefficient directeur** (pente).
> - $p$ est l'**ordonnée à l'origine**.
> - Un vecteur directeur est $\vec{u} = \begin{pmatrix} 1 \\ m \end{pmatrix}$.
>
> Une droite verticale a une équation de la forme $x = c$.

### 3.2 Équation cartésienne

> [!important] Définition : Équation cartésienne
> Toute droite du plan admet une équation de la forme :
> $$ax + by + c = 0 \quad (a \text{ et } b \text{ non tous deux nuls})$$
> - Un **vecteur directeur** est $\vec{u} = \begin{pmatrix} -b \\ a \end{pmatrix}$.
> - Un **vecteur normal** est $\vec{n} = \begin{pmatrix} a \\ b \end{pmatrix}$.

### 3.3 Déterminer l'équation d'une droite

**Connaissant un point $A(x_A, y_A)$ et le coefficient directeur $m$ :**

$$y - y_A = m(x - x_A)$$

**Connaissant deux points $A(x_A, y_A)$ et $B(x_B, y_B)$ avec $x_A \neq x_B$ :**

$$m = \frac{y_B - y_A}{x_B - x_A}$$

> [!example] Exemple
> Droite passant par $A(1,3)$ et $B(4,9)$.
>
> $m = \frac{9-3}{4-1} = \frac{6}{3} = 2$
>
> $y - 3 = 2(x-1) \implies y = 2x + 1$
>
> Sous forme cartésienne : $2x - y + 1 = 0$.

### 3.4 Positions relatives de deux droites

> [!important] Droites parallèles et perpendiculaires
> Soient $(d_1) : y = m_1 x + p_1$ et $(d_2) : y = m_2 x + p_2$.
>
> - $(d_1) \parallel (d_2) \iff m_1 = m_2$
>   - Si de plus $p_1 = p_2$ : droites confondues.
>   - Si $p_1 \neq p_2$ : droites strictement parallèles.
> - $(d_1) \perp (d_2) \iff m_1 \times m_2 = -1$

Sous forme cartésienne $(a_1 x + b_1 y + c_1 = 0)$ et $(a_2 x + b_2 y + c_2 = 0)$ :
- Parallèles $\iff a_1 b_2 - a_2 b_1 = 0$ (vecteurs directeurs colinéaires)
- Perpendiculaires $\iff a_1 a_2 + b_1 b_2 = 0$ (vecteurs normaux orthogonaux)


## 4. Produit scalaire (Première)

### 4.1 Définition

> [!important] Définition : Produit scalaire
> Le **produit scalaire** de deux vecteurs $\vec{u}$ et $\vec{v}$ est le nombre réel :
> $$\vec{u} \cdot \vec{v} = \|\vec{u}\| \times \|\vec{v}\| \times \cos(\vec{u}, \vec{v})$$
>
> Si $\vec{u} = \begin{pmatrix} x \\ y \end{pmatrix}$ et $\vec{v} = \begin{pmatrix} x' \\ y' \end{pmatrix}$ dans un repère orthonormé :
> $$\vec{u} \cdot \vec{v} = xx' + yy'$$

### 4.2 Autres expressions

> [!tip] Formules alternatives
> 1. **Avec le projeté orthogonal :** Si $H$ est le projeté orthogonal de $B$ sur $(OA)$ :
>    $\vec{u} \cdot \vec{v} = \|\vec{u}\| \times OH'$ (avec le signe de $\overrightarrow{OH'}$)
>
> 2. **Formules de polarisation :**
>    $$\vec{u} \cdot \vec{v} = \frac{1}{2}\left(\|\vec{u}+\vec{v}\|^2 - \|\vec{u}\|^2 - \|\vec{v}\|^2\right)$$
>    $$\vec{u} \cdot \vec{v} = \frac{1}{2}\left(\|\vec{u}\|^2 + \|\vec{v}\|^2 - \|\vec{u}-\vec{v}\|^2\right)$$

### 4.3 Propriétés

Pour tous vecteurs $\vec{u}$, $\vec{v}$, $\vec{w}$ et tout réel $k$ :

1. **Symétrie :** $\vec{u} \cdot \vec{v} = \vec{v} \cdot \vec{u}$
2. **Bilinéarité :** $\vec{u} \cdot (\vec{v} + \vec{w}) = \vec{u} \cdot \vec{v} + \vec{u} \cdot \vec{w}$
3. $(k\vec{u}) \cdot \vec{v} = k(\vec{u} \cdot \vec{v})$
4. $\vec{u} \cdot \vec{u} = \|\vec{u}\|^2$ (on note aussi $\vec{u}^2$)

### 4.4 Orthogonalité

> [!important] Critère d'orthogonalité
> Deux vecteurs $\vec{u}$ et $\vec{v}$ sont **orthogonaux** si et seulement si :
> $$\vec{u} \cdot \vec{v} = 0$$
> Notation : $\vec{u} \perp \vec{v}$.

### 4.5 Angle entre deux vecteurs

> [!important] Formule de l'angle
> $$\cos(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \times \|\vec{v}\|}$$

> [!example] Exemple
> $\vec{u} = \begin{pmatrix} 3 \\ 1 \end{pmatrix}$ et $\vec{v} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}$
>
> $\vec{u} \cdot \vec{v} = 3 \times 1 + 1 \times 2 = 5$
>
> $\|\vec{u}\| = \sqrt{10}$, $\|\vec{v}\| = \sqrt{5}$
>
> $\cos(\vec{u}, \vec{v}) = \frac{5}{\sqrt{10} \times \sqrt{5}} = \frac{5}{\sqrt{50}} = \frac{5}{5\sqrt{2}} = \frac{1}{\sqrt{2}}$
>
> Donc l'angle entre $\vec{u}$ et $\vec{v}$ est $\frac{\pi}{4}$ (soit $45°$).

### 4.6 Projeté orthogonal

> [!important] Projeté orthogonal
> Le **projeté orthogonal** $H$ du point $M$ sur la droite $(AB)$ est le point de $(AB)$ tel que $\overrightarrow{HM} \perp \overrightarrow{AB}$.
>
> Le vecteur $\overrightarrow{AH}$ est la projection de $\overrightarrow{AM}$ sur $\overrightarrow{AB}$ :
> $$\overrightarrow{AH} = \frac{\overrightarrow{AM} \cdot \overrightarrow{AB}}{\|\overrightarrow{AB}\|^2}\,\overrightarrow{AB}$$

### Visualisation animée (Manim)

> [!note] Ce que montre l'animation
> On trace deux vecteurs $\vec{u}$ et $\vec{v}$ de même origine. Le **projeté orthogonal** $H$ de l'extrémité de $\vec{v}$ sur la droite portée par $\vec{u}$ donne le vecteur $\overrightarrow{OH}$ (en jaune), avec l'angle droit matérialisé par la hauteur en pointillés. Le produit scalaire vaut alors $\vec{u}\cdot\vec{v} = \|\vec{u}\|\times \overline{OH}$ : la projection est l'interprétation géométrique du produit scalaire.

```manim
# Rendu : manimgl projete.py ProjeteOrthogonal
from manimlib import *
import numpy as np


class ProjeteOrthogonal(Scene):
    def construct(self):
        plan = NumberPlane(x_range=(-1, 6), y_range=(-1, 4))
        self.play(ShowCreation(plan))
        O = plan.c2p(0, 0)

        uvec, vvec = np.array([4, 1]), np.array([2, 3])
        u = Arrow(O, plan.c2p(*uvec), buff=0, color=BLUE)
        v = Arrow(O, plan.c2p(*vvec), buff=0, color=GREEN)
        ulab = Tex(r"\vec{u}", color=BLUE).next_to(plan.c2p(*uvec), DR, buff=0.1)
        vlab = Tex(r"\vec{v}", color=GREEN).next_to(plan.c2p(*vvec), UL, buff=0.1)
        self.play(GrowArrow(u), GrowArrow(v), Write(ulab), Write(vlab))
        self.wait()

        # Projeté orthogonal H de v sur la droite portée par u
        t = np.dot(uvec, vvec) / np.dot(uvec, uvec)
        Hp = plan.c2p(*(t * uvec))
        proj = Arrow(O, Hp, buff=0, color=YELLOW)
        hauteur = DashedLine(plan.c2p(*vvec), Hp, color=GREY_B)
        Hdot = Dot(Hp, color=YELLOW)
        Hlab = Tex("H").next_to(Hp, DOWN, buff=0.15)
        self.play(ShowCreation(hauteur), GrowArrow(proj), FadeIn(Hdot), Write(Hlab))

        formule = Tex(r"\vec{u}\cdot\vec{v} = \|\vec{u}\|\times \overline{OH}")
        formule.to_edge(UP).set_backstroke()
        self.play(Write(formule))
        self.wait(2)
```

### 4.7 Équation de cercle

Dans un repère orthonormé, le cercle de centre $\Omega(a,b)$ et de rayon $r$ a pour équation :

$$(x-a)^2 + (y-b)^2 = r^2$$

Forme développée : $x^2 + y^2 - 2ax - 2by + a^2 + b^2 - r^2 = 0$.
