---
title: "Glossaire des Symboles Mathématiques"
domain: "Applied Sciences"
subdomain: "Mathematics"
tags: [sciences-appliquées, mathématiques, glossaire, notation, symboles]
date: "2026-05-20"
---

# Glossaire des Symboles Mathématiques

Les mathématiques ont leur alphabet : un système de symboles concis qui condense en quelques signes ce qu'il faudrait des phrases pour exprimer. Cette note recense les symboles courants, leur **lecture** orale (importante en colle), leur **signification**, et un exemple d'usage.

> [!tip] Comment lire les maths à voix haute
> En colle, en oral, ou simplement pour ne pas se tromper en relisant son cours, savoir lire les formules en français est essentiel. Cette note te donne la prononciation conventionnelle de chaque symbole.

## Logique

| Symbole | Lecture | Signification | Exemple |
|---|---|---|---|
| $\forall$ | « pour tout » | Quantificateur universel | $\forall x \in \mathbb{R},\; x^2 \geq 0$ |
| $\exists$ | « il existe » | Quantificateur existentiel | $\exists n \in \mathbb{N},\; n > 1000$ |
| $\exists!$ | « il existe un unique » | Existence et unicité | $\exists! x,\; x + 1 = 2$ |
| $\Rightarrow$ | « implique » | Implication logique | $x > 1 \Rightarrow x^2 > 1$ |
| $\Leftarrow$ | « est impliqué par » / « si » | Implication réciproque | rarement écrit, on retourne $\Rightarrow$ |
| $\Leftrightarrow$ | « si et seulement si » / « équivaut à » | Équivalence | $x^2 = 1 \Leftrightarrow x = \pm 1$ |
| $\lnot$ ou $\neg$ | « non » | Négation | $\lnot(x > 0) \equiv x \leq 0$ |
| $\land$ | « et » | Conjonction | $P \land Q$ : $P$ et $Q$ vraies |
| $\lor$ | « ou » (inclusif) | Disjonction | $P \lor Q$ : au moins une vraie |
| $\equiv$ | « équivalent » | Équivalence sémantique (ou congruence) | $P \equiv Q$ |
| $\vdash$ | « démontre » / « thèse » | Déduction syntaxique | $\Gamma \vdash \varphi$ |
| $\models$ | « satisfait » | Vérité sémantique | $\mathcal{M} \models \varphi$ |
| $\Box$, $\blacksquare$, CQFD | « ce qu'il fallait démontrer » | Fin de démonstration | « … donc $f$ est continue. $\blacksquare$ » |

> [!warning] Pièges courants
> - $P \Rightarrow Q$ et $Q \Rightarrow P$ **ne sont pas équivalents** — la première dit « si $P$ alors $Q$ », la seconde dit l'inverse
> - $\Rightarrow$ n'est pas synonyme de « donc » : on peut écrire « $P \Rightarrow Q$ est vraie » indépendamment de la vérité de $P$
> - L'ordre $\forall x,\; \exists y$ vs $\exists y,\; \forall x$ change radicalement le sens

## Ensembles

| Symbole | Lecture | Signification | Exemple |
|---|---|---|---|
| $\in$ | « appartient à » | Élément d'un ensemble | $3 \in \mathbb{N}$ |
| $\notin$ | « n'appartient pas à » | Non-appartenance | $-1 \notin \mathbb{N}$ |
| $\subset$ | « est inclus dans » | Inclusion (large ou stricte selon convention) | $\mathbb{N} \subset \mathbb{Z}$ |
| $\subseteq$ | « est inclus ou égal » | Inclusion large | $A \subseteq A$ toujours |
| $\subsetneq$ | « est strictement inclus » | Inclusion stricte | $\mathbb{N} \subsetneq \mathbb{Z}$ |
| $\supset$ | « contient » | Inclusion inverse | $\mathbb{Z} \supset \mathbb{N}$ |
| $\cup$ | « union » | Union ensembliste | $A \cup B$ |
| $\cap$ | « inter » / « intersection » | Intersection | $A \cap B$ |
| $\setminus$ | « privé de » | Différence | $A \setminus B = \{x \in A : x \notin B\}$ |
| $\complement A$, $\overline{A}$, $A^c$ | « complémentaire de A » | Complémentaire | $\complement_{\mathbb{R}}\mathbb{Q}$ = irrationnels |
| $\varnothing$, $\emptyset$ | « ensemble vide » | Ensemble sans élément | $A \cap \overline{A} = \varnothing$ |
| $|A|$, $\text{card}(A)$ | « cardinal de A » | Nombre d'éléments | $|\{1, 2, 3\}| = 3$ |
| $\mathcal{P}(A)$ | « parties de A » | Ensemble des parties | $|\mathcal{P}(A)| = 2^{|A|}$ |
| $A \times B$ | « A croix B » | Produit cartésien | $\mathbb{R}^2 = \mathbb{R} \times \mathbb{R}$ |
| $\{x : P(x)\}$ | « l'ensemble des x tels que P(x) » | Notation par compréhension | $\{n \in \mathbb{N} : n^2 < 100\}$ |

## Ensembles numériques

| Symbole | Lecture | Définition |
|---|---|---|
| $\mathbb{N}$ | « N » | Entiers naturels : $\{0, 1, 2, \dots\}$ |
| $\mathbb{Z}$ | « Z » | Entiers relatifs : $\{\dots, -2, -1, 0, 1, 2, \dots\}$ |
| $\mathbb{D}$ | « D » | Nombres décimaux |
| $\mathbb{Q}$ | « Q » | Rationnels : $\{p/q : p \in \mathbb{Z}, q \in \mathbb{N}^*\}$ |
| $\mathbb{R}$ | « R » | Réels |
| $\mathbb{C}$ | « C » | Complexes : $\{a + ib : a, b \in \mathbb{R}\}$ |
| $\mathbb{H}$ | « H » (Hamilton) | Quaternions |
| $\mathbb{R}^*, \mathbb{R}^+, \mathbb{R}^*_+$ | « R étoile, R plus, R étoile plus » | Privé de 0, positifs, strictement positifs |
| $\mathbb{F}_q$ | « corps fini à q éléments » | Corps fini |
| $\mathbb{K}$ ou $K$ | « K » | Corps quelconque (souvent $\mathbb{R}$ ou $\mathbb{C}$) |

## Opérations et relations

| Symbole | Lecture | Signification |
|---|---|---|
| $=$ | « égal » | Égalité |
| $\neq$ | « différent » | Inégalité |
| $\leq$ | « inférieur ou égal » | Inégalité large |
| $<$ | « strictement inférieur » | Inégalité stricte |
| $\geq, >$ | « supérieur ou égal, strictement supérieur » | — |
| $\approx$ | « environ » | Approximation numérique |
| $\sim$ | « équivalent » | Asymptotique : $u_n \sim v_n$ ssi $u_n/v_n \to 1$ |
| $\propto$ | « proportionnel » | Proportionnalité |
| $\equiv \pmod n$ | « congru modulo n » | $a \equiv b \pmod n$ ssi $n \mid (a-b)$ |
| $\mid$ | « divise » | $a \mid b$ ssi $\exists k,\; b = ka$ |
| $\nmid$ | « ne divise pas » | — |
| $\gcd$, $\pgcd$, $\wedge$ | « pgcd » | Plus grand commun diviseur |
| $\text{lcm}$, $\ppcm$, $\vee$ | « ppcm » | Plus petit commun multiple |
| $\circ$ | « rond » | Composition : $(f \circ g)(x) = f(g(x))$ |
| $\cdot$ | « point » | Produit (souvent omis) |
| $\otimes$ | « tenseur » | Produit tensoriel |
| $\oplus$ | « somme directe » | $E = F \oplus G$ |
| $\perp$ | « orthogonal » | $u \perp v$ : $\langle u, v \rangle = 0$ |
| $\parallel$ | « parallèle » | Droites parallèles |

## Sommes, produits, limites

| Symbole | Lecture | Signification |
|---|---|---|
| $\sum_{k=1}^n a_k$ | « somme de k égal 1 à n de a indice k » | $a_1 + a_2 + \cdots + a_n$ |
| $\prod_{k=1}^n a_k$ | « produit de k égal 1 à n de a indice k » | $a_1 \cdot a_2 \cdots a_n$ |
| $\int_a^b f(x)\, dx$ | « intégrale de a à b de f(x) dx » | Intégrale définie |
| $\iint, \iiint$ | « double / triple intégrale » | Intégrale multiple |
| $\oint$ | « intégrale curviligne fermée » | Intégrale sur courbe fermée |
| $\lim_{n \to +\infty}$ | « limite quand n tend vers plus l'infini » | — |
| $\liminf$, $\limsup$ | « limite inférieure / supérieure » | Limites d'adhérence |
| $\to$, $\rightarrow$ | « tend vers », « flèche » | $u_n \to \ell$ |
| $\mapsto$ | « est associé à » | $x \mapsto f(x)$ : définition d'application |

## Calcul différentiel et intégral

| Symbole | Lecture | Signification |
|---|---|---|
| $f'(x)$, $\frac{df}{dx}$ | « f prime de x », « d f sur d x » | Dérivée |
| $f''$, $f^{(n)}$ | « f seconde », « f n-ième » | Dérivées successives |
| $\partial f / \partial x$ | « d rond f sur d rond x » | Dérivée partielle |
| $\nabla f$ | « nabla f » / « gradient de f » | Gradient |
| $\Delta f$ | « delta f » / « laplacien de f » | Laplacien $\sum \partial^2 f / \partial x_i^2$ |
| $\text{div}, \text{rot}, \text{curl}$ | « divergence, rotationnel » | Opérateurs vectoriels |
| $df$ | « différentielle de f » | — |
| $o(f)$, $O(f)$ | « petit o de f », « grand O de f » | Notations de Landau (négligeable / dominé) |

## Algèbre linéaire

| Symbole | Lecture | Signification |
|---|---|---|
| $\dim E$ | « dimension de E » | — |
| $\text{rg}(f)$ | « rang de f » | $\dim(\text{Im } f)$ |
| $\ker f$ | « noyau de f » | $\{x : f(x) = 0\}$ |
| $\text{Im } f$ | « image de f » | $\{f(x) : x \in E\}$ |
| $\text{Vect}(v_1, \dots, v_k)$ | « espace engendré par » | Sous-espace engendré |
| $\mathcal{L}(E, F)$ | « les applications linéaires de E dans F » | — |
| $\mathcal{L}(E) = \mathcal{L}(E, E)$ | « endomorphismes de E » | — |
| $\text{GL}_n(K)$ | « groupe linéaire » | Matrices inversibles |
| $\text{tr}(A)$ | « trace de A » | Somme des éléments diagonaux |
| $\det(A)$, $|A|$ | « déterminant de A » | — |
| $A^T$, $A^t$, $\,^tA$ | « transposée de A » | — |
| $A^{-1}$ | « A à la moins un » | Matrice inverse |
| $A^*$, $\bar{A}^T$ | « adjointe » / « hermitienne » | Conjuguée transposée |
| $I_n$, $\text{Id}$ | « identité » | Matrice identité |
| $\langle u, v \rangle$, $u \cdot v$ | « produit scalaire » | — |
| $\|u\|$ | « norme de u » | — |

## Probabilités

| Symbole | Lecture | Signification |
|---|---|---|
| $\Omega$ | « oméga » | Univers (ensemble des issues) |
| $\mathcal{A}$ | « tribu, sigma-algèbre » | Famille des événements |
| $P(A)$, $\mathbb{P}(A)$ | « P de A », « probabilité de A » | — |
| $P(A \mid B)$ | « P de A sachant B » | Probabilité conditionnelle |
| $E(X)$, $\mathbb{E}(X)$ | « espérance de X » | — |
| $V(X)$, $\text{Var}(X)$ | « variance de X » | — |
| $\sigma(X)$ | « écart-type de X » | — |
| $\text{cov}(X, Y)$ | « covariance » | — |
| $X \sim \mathcal{N}(\mu, \sigma^2)$ | « X suit une loi normale » | — |
| $X \perp\!\!\!\perp Y$ | « X et Y indépendantes » | Notation pour l'indépendance |
| $X_n \xrightarrow{\mathcal{L}} X$ | « convergence en loi » | — |
| $X_n \xrightarrow{P} X$ | « convergence en probabilité » | — |
| $X_n \xrightarrow{p.s.} X$ | « convergence presque sûre » | — |

## Lettres grecques courantes

| Lettre | Nom | Usage typique |
|---|---|---|
| $\alpha$, $\beta$, $\gamma$ | alpha, bêta, gamma | Coefficients, angles |
| $\delta$, $\Delta$ | delta | Petite variation, opérateur Laplacien (capitale) |
| $\varepsilon$, $\epsilon$ | epsilon | Petite quantité positive (épsilon-delta) |
| $\zeta$ | zêta | Fonction zêta de Riemann |
| $\eta$ | êta | Variable auxiliaire |
| $\theta$, $\Theta$ | thêta | Angle, paramètre statistique |
| $\iota$ | iota | Rare |
| $\kappa$ | kappa | Courbure, constante |
| $\lambda$, $\Lambda$ | lambda | Valeur propre, paramètre Poisson |
| $\mu$ | mu | Moyenne, mesure |
| $\nu$ | nu | Mesure, fréquence |
| $\xi$, $\Xi$ | ksi, xi | Variable auxiliaire |
| $\pi$, $\Pi$ | pi | Constante 3.14, produit (capitale) |
| $\rho$ | rho | Densité, coefficient de corrélation |
| $\sigma$, $\Sigma$ | sigma | Écart-type, somme (capitale) |
| $\tau$ | tau | Temps, période |
| $\varphi$, $\phi$, $\Phi$ | phi | Indicatrice d'Euler, angle, fonction |
| $\chi$ | khi | Loi du khi-2, polynôme caractéristique |
| $\psi$, $\Psi$ | psi | Fonction d'onde, fonction quelconque |
| $\omega$, $\Omega$ | oméga | Pulsation, univers (capitale) |

## Quelques notations spéciales

| Symbole | Lecture | Signification |
|---|---|---|
| $\binom{n}{k}$ | « combinaison de k parmi n » / « k parmi n » | $\frac{n!}{k!(n-k)!}$ |
| $n!$ | « factorielle n » | $n \cdot (n-1) \cdots 1$ |
| $\lfloor x \rfloor$ | « partie entière de x » / « plancher de x » | Plus grand entier $\leq x$ |
| $\lceil x \rceil$ | « plafond de x » | Plus petit entier $\geq x$ |
| $\lfloor x \rceil$ | « entier le plus proche » | — |
| $\{x\}$ | « partie fractionnaire » | $x - \lfloor x \rfloor$ |
| $|x|$ | « valeur absolue de x » | — |
| $\overline{z}$ | « conjugué de z » | Conjugué complexe |
| $\text{Re}(z), \text{Im}(z)$ | « partie réelle, imaginaire » | — |
| $\arg(z)$ | « argument de z » | Angle |
| $\delta_{ij}$ | « delta de Kronecker » | 1 si $i = j$, 0 sinon |
| $\mathbb{1}_A(x)$, $\chi_A(x)$ | « fonction indicatrice de A » | 1 si $x \in A$, 0 sinon |
| $\sup$, $\inf$ | « sup, inf » | Borne supérieure/inférieure |
| $\max$, $\min$ | « max, min » | Maximum, minimum |
| $\arg\max$, $\arg\min$ | « arg-max, arg-min » | Argument qui maximise/minimise |

## Conventions typographiques

- **Caractères droits** pour les fonctions standards : $\sin$, $\cos$, $\log$, $\det$, $\ker$, $\dim$
- **Lettres calligraphiques** $\mathcal{A}, \mathcal{B}, \dots$ pour les familles/catégories
- **Lettres ajourées (blackboard)** $\mathbb{N}, \mathbb{R}, \dots$ pour les ensembles numériques de référence
- **Lettres gothiques** $\mathfrak{g}, \mathfrak{h}, \dots$ en algèbre avancée (algèbres de Lie, idéaux)
- **Indices** pour les éléments d'une suite/famille : $u_n$, $a_{ij}$
- **Exposants** pour les puissances ou itérations : $x^n$, $f^{(n)}$, $A^T$ (transposée — l'exposant peut avoir un autre sens)
