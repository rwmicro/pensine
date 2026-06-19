---
title: "Comment Montrer Que…"
domain: "Applied Sciences"
subdomain: "Mathematics"
tags: [sciences-appliquées, mathématiques, méthodologie, exercices, recettes]
date: "2026-05-20"
---
# Comment Montrer Que…

Face à une question d'exercice, le blocage initial vient rarement du manque de connaissance — il vient de **ne pas savoir par quel bout commencer**. Cette note est un index pratique : pour chaque type de question fréquente, elle indique la(les) méthode(s) standard à essayer. C'est un **réflexe à acquérir**, pas une vérité absolue : parfois la méthode standard ne marche pas, mais c'est presque toujours par là qu'il faut commencer.

> [!tip] Mode d'emploi
> Tu lis « montrer que… » dans un sujet ? Cherche le pattern le plus proche dans la table des matières ci-dessous, applique la recette, et adapte.

## Sommaire des questions classiques

- [Analyse — fonctions](#analyse--fonctions)
- [Analyse — suites et séries](#analyse--suites-et-séries)
- [Analyse — intégrales](#analyse--intégrales)
- [Algèbre linéaire](#algèbre-linéaire)
- [Arithmétique](#arithmétique)
- [Probabilités](#probabilités)
- [Ensembles et applications](#ensembles-et-applications)

## Analyse — fonctions

### Montrer qu'une fonction est continue en $a$

**Méthodes possibles** :
1. **Composition** : si $f$ est continue en $a$ et $g$ continue en $f(a)$, alors $g \circ f$ continue en $a$
2. **Somme/produit/quotient** de fonctions continues (attention au dénominateur)
3. **Définition $\varepsilon$-$\delta$** : $\forall \varepsilon > 0,\; \exists \delta > 0,\; |x - a| < \delta \Rightarrow |f(x) - f(a)| < \varepsilon$ (rare en pratique)
4. **Caractérisation séquentielle** : pour toute suite $(x_n) \to a$, $f(x_n) \to f(a)$
5. **Limite à droite = limite à gauche = $f(a)$** (utile aux raccords)

### Montrer qu'une fonction est dérivable

1. **Théorèmes généraux** : somme, produit, composition, quotient de fonctions dérivables
2. **Définition** : $\lim_{h \to 0} \frac{f(a+h) - f(a)}{h}$ existe et est finie
3. **Prolongement** : si $f$ est définie par morceaux, vérifier le raccord (limite des dérivées à gauche/droite)

### Montrer qu'une fonction est de classe $\mathcal{C}^k$ ou $\mathcal{C}^\infty$

Récurrence sur l'ordre de dérivation, ou théorèmes généraux. Pour $\mathcal{C}^\infty$, souvent par **identification** avec une fonction connue (exponentielle, polynôme, série entière sur son disque ouvert).

### Montrer qu'une fonction est bijective

1. **Stricte monotonie sur un intervalle** + **théorème de la bijection** (TVI + monotonie)
2. **Construction explicite de la réciproque**
3. **Injectivité et surjectivité séparément** :
   - Injectivité : $f(x) = f(y) \Rightarrow x = y$ (souvent par stricte monotonie)
   - Surjectivité : pour tout $y$ dans l'arrivée, exhiber $x$ tel que $f(x) = y$ (souvent par TVI)

### Montrer qu'une équation $f(x) = 0$ admet une solution

1. **TVI** : si $f$ continue et change de signe
2. **Théorème de la bijection** + valeur cible dans l'image

### Montrer qu'une équation $f(x) = 0$ admet une **unique** solution

TVI + **stricte monotonie** (assurée par étude du signe de $f'$).

### Montrer qu'une fonction est paire / impaire / périodique

**Calcul direct** : $f(-x) = f(x)$ / $f(-x) = -f(x)$ / $f(x+T) = f(x)$.
Vérifier d'abord que le domaine est symétrique (ou stable par translation).

### Montrer une inégalité $f(x) \geq g(x)$

1. **Étudier $h = f - g$** : montrer $h \geq 0$ via tableau de variations + valeur minimum positive
2. **Récurrence** si l'inégalité dépend d'un entier $n$
3. **Inégalité connue** : Cauchy-Schwarz, Bernoulli, AM-GM, convexité
4. **Encadrement** : montrer $f \geq h \geq g$ pour une fonction intermédiaire $h$

### Montrer qu'une limite existe

1. **Calcul direct** par opérations sur les limites
2. **Encadrement** (théorème des gendarmes)
3. **Suite monotone bornée** (pour les suites)
4. **Critère de Cauchy** (analyse plus fine)

## Analyse — suites et séries

### Montrer qu'une suite converge

1. **Suite monotone et bornée** ⇒ convergente
2. **Suites adjacentes** ($u_n$ croît, $v_n$ décroît, $v_n - u_n \to 0$)
3. **Encadrement** par deux suites de même limite
4. **Convergence dans $\mathbb{R}$** d'une suite de Cauchy (rare au niveau prépa)
5. **Identification** avec une suite connue (géométrique, arithmético-géométrique, série télescopique)

### Montrer qu'une suite diverge

1. **Limite infinie** : minoration/majoration par une suite divergente
2. **Deux sous-suites de limites différentes**
3. **Critère négatif** : $u_n$ non bornée, ou non monotone et non bornée

### Montrer qu'une série $\sum u_n$ converge

1. **Convergence absolue** ($\sum |u_n|$ converge) ⇒ convergence
2. **Comparaison** avec une série de référence ($\sum 1/n^\alpha$, géométrique, $\sum 1/n!$)
3. **Critère de d'Alembert** : $u_{n+1}/u_n \to \ell < 1$ ⇒ converge
4. **Critère de Cauchy** : $\sqrt[n]{|u_n|} \to \ell < 1$ ⇒ converge
5. **Séries alternées** : $u_n = (-1)^n a_n$ avec $a_n$ décroissante vers 0 ⇒ converge
6. **Équivalent** : si $u_n \sim v_n$ et signes constants, mêmes natures

### Montrer une convergence uniforme

1. **Majoration uniforme** : $\sup_{x} |f_n(x) - f(x)| \to 0$
2. **Critère de Weierstrass** pour les séries : $|u_n(x)| \leq a_n$ avec $\sum a_n$ convergente
3. **Cauchy uniforme**

## Analyse — intégrales

### Montrer qu'une intégrale converge (intégrale impropre)

1. **Comparaison** avec $\int 1/x^\alpha$
2. **Équivalent** à l'infini (signes constants)
3. **Critère de Riemann** : en $+\infty$, $\int_1^{+\infty} \frac{dx}{x^\alpha}$ converge ssi $\alpha > 1$ ; en $0$, $\int_0^1 \frac{dx}{x^\alpha}$ converge ssi $\alpha < 1$
4. **Convergence absolue** ⇒ convergence

### Montrer qu'une fonction est intégrable sur $I$

Sur $[a, b]$ fermé borné : continue ou continue par morceaux suffit.
Sur intervalle non borné : convergence de l'intégrale (cf. ci-dessus).

### Calculer une intégrale

1. **Primitive directe** (formulaire)
2. **Intégration par parties** (IPP) : $\int u'v = [uv] - \int uv'$
3. **Changement de variable**
4. **Décomposition en éléments simples** (fractions rationnelles)
5. **Linéarisation** trigonométrique
6. **Symétries** (fonction paire/impaire)
7. **Astuces** : différentiation sous l'intégrale, équations différentielles vérifiées par l'intégrale

## Algèbre linéaire

### Montrer qu'un ensemble $F$ est un sous-espace vectoriel

**Trois conditions** :
1. $F \subset E$ et $F \neq \varnothing$ (souvent : $0_E \in F$)
2. Stable par addition : $u, v \in F \Rightarrow u + v \in F$
3. Stable par multiplication par scalaire : $u \in F,\; \lambda \in K \Rightarrow \lambda u \in F$

**Variante condensée** : $F \neq \varnothing$ et $\forall u, v \in F,\; \forall \lambda \in K,\; u + \lambda v \in F$.

### Montrer qu'une famille est libre

1. **Définition** : $\sum \lambda_i x_i = 0 \Rightarrow \lambda_i = 0$ pour tout $i$
2. **Matrice associée** de rang égal au nombre de vecteurs (cas concret en dim. finie)
3. **Wronskien** pour des fonctions (cas particulier des $\mathcal{C}^\infty$)
4. **Échelle** : famille échelonnée en degré (polynômes) ou en valuation est libre

### Montrer qu'une famille est génératrice

Montrer que tout vecteur de $E$ s'écrit comme combinaison linéaire de la famille. En dim. finie : suffisant d'avoir $\dim E$ vecteurs libres.

### Montrer qu'une famille est une base

1. **Libre et génératrice**
2. En **dimension finie** : libre et **cardinal = dim**, ou génératrice et cardinal = dim

### Montrer qu'une application est linéaire

$f(u + \lambda v) = f(u) + \lambda f(v)$ pour tous $u, v \in E$ et $\lambda \in K$.

### Calculer un rang, un noyau, une image

- $\ker f = \{x \in E : f(x) = 0\}$ — résoudre le système $f(x) = 0$
- $\text{Im } f = \{f(x) : x \in E\}$ — image des vecteurs d'une base
- **Théorème du rang** : $\dim E = \dim \ker f + \text{rg}(f)$

### Montrer qu'une matrice est diagonalisable

1. **Polynôme caractéristique scindé à racines simples** ⇒ diagonalisable
2. **Polynôme caractéristique scindé** + dimension des sous-espaces propres = ordre de multiplicité
3. **Polynôme annulateur scindé à racines simples**
4. **Symétrique réelle** (théorème spectral)

## Arithmétique

### Montrer que $a \mid b$

1. **Définition** : exhiber $k$ tel que $b = ka$
2. **Bézout** : $\gcd(a, c) = 1$ et $a \mid bc$ ⇒ $a \mid b$ (théorème de Gauss)
3. **Congruences** : $b \equiv 0 \pmod a$

### Montrer que $\gcd(a, b) = d$

1. $d \mid a$ et $d \mid b$
2. Pour tout diviseur commun $c$, $c \mid d$
3. Algorithme d'Euclide

### Montrer que $a$ et $b$ sont premiers entre eux

1. $\gcd(a, b) = 1$ (Euclide)
2. **Bézout** : exhiber $u, v$ tels que $au + bv = 1$
3. **Pas de diviseur premier commun**

### Montrer qu'un entier est premier

Vérifier qu'aucun premier $\leq \sqrt{n}$ ne divise $n$.

### Montrer une congruence $a \equiv b \pmod n$

1. $n \mid (a - b)$
2. **Petit théorème de Fermat** (si $n$ premier)
3. **Théorème d'Euler**
4. **Théorème des restes chinois** pour décomposer modulo des facteurs premiers entre eux

## Probabilités

### Montrer que deux événements sont indépendants

$P(A \cap B) = P(A) \cdot P(B)$ (définition).

### Montrer une formule de probabilité totale

Identifier un **système complet d'événements** $(B_i)$ (partition de $\Omega$) et appliquer :
$$P(A) = \sum_i P(A \mid B_i) \cdot P(B_i)$$

### Montrer qu'une variable aléatoire suit une certaine loi

1. **Identifier la situation** (Bernoulli, binomiale, géométrique, Poisson, normale)
2. **Calculer la loi** : $P(X = k)$ pour $k$ dans le support
3. **Vérifier** que c'est bien la loi en question

### Calculer espérance et variance

1. **Définition** : $E(X) = \sum k \cdot P(X = k)$ ; $V(X) = E((X-E(X))^2)$
2. **Formule de König-Huygens** : $V(X) = E(X^2) - E(X)^2$
3. **Linéarité de l'espérance** : $E(X + Y) = E(X) + E(Y)$ même non indépendantes
4. **Pour variances** : indépendance requise, $V(X+Y) = V(X) + V(Y)$ ssi indépendantes

## Ensembles et applications

### Montrer que $A = B$ (ensembles)

**Double inclusion** : $A \subset B$ et $B \subset A$.

### Montrer qu'une application est injective

$f(x) = f(y) \Rightarrow x = y$. (Toujours partir de $f(x) = f(y)$.)

### Montrer qu'une application est surjective

Pour tout $y$ dans l'arrivée, **construire** $x$ tel que $f(x) = y$ (souvent par résolution d'équation).

### Montrer qu'une application est bijective

1. **Injective et surjective**
2. **Réciproque explicite** $g$ telle que $f \circ g = \text{id}$ et $g \circ f = \text{id}$
3. **En dim. finie** : injectivité ssi surjectivité ssi bijectivité (pour endomorphisme)

## Conseils méta

> [!tip] Réflexes utiles
> - **Toujours commencer par écrire l'énoncé sur sa copie** — pas de manipulation tête baissée
> - **Identifier le type d'objet** (fonction, suite, ensemble, application) — la méthode dépend du type
> - **Si bloqué pendant 5 minutes**, écrire la **négation** de ce qu'on cherche à montrer — parfois ça débloque
> - **Tester sur un petit cas** (n = 1, dimension 2) avant de généraliser
> - **Faire un dessin** si géométrie ou analyse (graphe de fonction)
> - **Toujours conclure** par « par conséquent… » ou « CQFD » — sinon la copie semble inachevée

Pour les méthodes générales, voir [[Méthodes de Démonstration]]. Pour les preuves modèles à imiter, voir [[Démonstrations Classiques]].
