---
title: "Erreurs Classiques en Mathématiques"
domain: "Applied Sciences"
subdomain: "Mathematics"
tags: [sciences-appliquées, mathématiques, erreurs, pièges, méthodologie]
date: "2026-05-20"
---

# Erreurs Classiques en Mathématiques

Les erreurs en mathématiques ne sont pas aléatoires : la plupart suivent quelques patrons récurrents. Cette note recense les pièges les plus courants — ceux qu'on voit semaine après semaine en copies de prépa, et qui font perdre des points alors que le raisonnement de fond était bon. **Connaître l'erreur, c'est déjà l'éviter.**

> [!tip] Mode d'emploi
> Avant de rendre une copie ou un DM : relis-la en cherchant **activement** les erreurs listées ici. C'est plus efficace qu'une relecture passive.

## 1. Erreurs de logique

### 1.1 Confondre implication et équivalence

L'erreur la plus répandue : démontrer $P \Rightarrow Q$ et en conclure $P \Leftrightarrow Q$.

> [!warning] $P \Rightarrow Q$ **ne donne pas** $Q \Rightarrow P$
> Exemple : « si $x = 2$ alors $x^2 = 4$ » est vrai. La réciproque « si $x^2 = 4$ alors $x = 2$ » est **fausse** ($x = -2$ marche aussi).

**Conséquence** : si l'énoncé demande une équivalence, on doit prouver **les deux sens**.

### 1.2 Négation mal posée

| Énoncé | Négation correcte | Erreur typique |
|---|---|---|
| $\forall x, P(x)$ | $\exists x, \lnot P(x)$ | « $\forall x, \lnot P(x)$ » (trop fort) |
| $\exists x, P(x)$ | $\forall x, \lnot P(x)$ | « $\exists x, \lnot P(x)$ » (n'est pas une négation) |
| $\forall x,\; \exists y,\; P(x,y)$ | $\exists x,\; \forall y,\; \lnot P(x,y)$ | Oublier de **renverser** les quantificateurs |
| $A$ et $B$ | non $A$ **ou** non $B$ (De Morgan) | « non $A$ et non $B$ » |
| $A$ ou $B$ | non $A$ **et** non $B$ (De Morgan) | « non $A$ ou non $B$ » |

### 1.3 Pétition de principe (raisonnement circulaire)

Utiliser ce qu'on doit démontrer pour le démontrer. Souvent caché derrière un « il est clair que ».

> [!example] Erreur
> Pour montrer $a^2 + b^2 \geq 2ab$, écrire :
> « On a $a^2 - 2ab + b^2 \geq 0$, soit $(a-b)^2 \geq 0$, **ce qui est vrai puisque $a^2 + b^2 \geq 2ab$**. »
> 
> *Problème* : on suppose ce qu'on cherche à prouver. La bonne preuve part de $(a-b)^2 \geq 0$ et **développe**.

### 1.4 Abus du « donc »

Le mot « donc » sous-entend une déduction logique. L'utiliser à la place d'un saut intuitif est une faute.

> [!warning] Phrases suspectes
> - « Il est clair que… » → s'il l'était, on n'aurait pas besoin de l'écrire
> - « On voit que… » → la copie ne voit pas, elle lit
> - « De même… » → écrire au moins la deuxième occurrence pour montrer qu'on sait

### 1.5 Confondre condition nécessaire et condition suffisante

- *Nécessaire* : « pour que $Q$, il faut $P$ » ($Q \Rightarrow P$)
- *Suffisante* : « pour que $Q$, il suffit que $P$ » ($P \Rightarrow Q$)

« Nécessaire et suffisante » = équivalence.

## 2. Erreurs algébriques

### 2.1 Manipulations interdites

| Faute | Pourquoi c'est faux |
|---|---|
| $\sqrt{a + b} = \sqrt{a} + \sqrt{b}$ | $\sqrt{1+1} = \sqrt{2} \neq 2$ |
| $(a + b)^2 = a^2 + b^2$ | Manque le double produit $2ab$ |
| $\frac{a + b}{c + d} = \frac{a}{c} + \frac{b}{d}$ | Test : $\frac{1+1}{1+1} = 1 \neq 2$ |
| $\frac{1}{a + b} = \frac{1}{a} + \frac{1}{b}$ | Test : $\frac{1}{2} \neq \frac{1}{1} + \frac{1}{1} = 2$ |
| $\ln(a + b) = \ln a + \ln b$ | Le logarithme transforme produit ↔ somme, pas somme ↔ somme |
| $e^{a + b} = e^a + e^b$ | C'est $e^a \cdot e^b$ |
| $\sin(a + b) = \sin a + \sin b$ | Formules d'addition non triviales |
| $(a^b)^c = a^{b+c}$ | C'est $a^{bc}$ |
| $a^b \cdot a^c = a^{bc}$ | C'est $a^{b+c}$ |

### 2.2 Division par zéro

> [!warning] Toujours vérifier que ce par quoi on divise est non nul
> Erreur célèbre :
> $$a = b \Rightarrow a^2 = ab \Rightarrow a^2 - b^2 = ab - b^2 \Rightarrow (a+b)(a-b) = b(a-b) \Rightarrow a + b = b$$
> 
> Conclusion absurde : si $a = b = 1$, alors $1 + 1 = 1$. L'erreur : on a divisé par $a - b$ qui est nul.

### 2.3 Simplifications hâtives

- Simplifier $\sqrt{x^2}$ en $x$ : faux, c'est $|x|$
- Simplifier $\ln(x^2)$ en $2 \ln x$ : valable seulement si $x > 0$ ; sinon $2 \ln |x|$
- Multiplier par un facteur d'expression négative dans une inégalité **sans renverser le sens**

### 2.4 Identités remarquables élargies

$$(a + b + c)^2 = a^2 + b^2 + c^2 + 2ab + 2ac + 2bc$$

Ne **pas oublier les doubles produits**, et **tous** les doubles produits.

## 3. Erreurs en analyse

### 3.1 Limite — confondre forme et résultat

Une « forme indéterminée » n'est pas une valeur de limite :
- $\frac{0}{0}$ : peut valoir n'importe quoi (par exemple, $\lim x/x = 1$, $\lim x^2/x = 0$, $\lim x/x^2 = \infty$)
- $\infty - \infty$ : $(n+1) - n \to 1$, mais $(2n) - n \to \infty$
- $0 \cdot \infty$, $\infty^0$, $1^\infty$, $0^0$ : toutes indéterminées

> [!warning] Conclusion hâtive
> « $\lim x \sin(1/x) = 0$ car c'est $0 \cdot$ (quelque chose) » est faux. Il faut **majorer** : $|x \sin(1/x)| \leq |x| \to 0$, puis utiliser les gendarmes.

### 3.2 Dérivée

| Erreur | Correction |
|---|---|
| $(f \cdot g)' = f' \cdot g'$ | $(fg)' = f'g + fg'$ |
| $(f/g)' = f'/g'$ | $(f/g)' = (f'g - fg')/g^2$ |
| $(f \circ g)' = f' \circ g'$ | $(f \circ g)' = (f' \circ g) \cdot g'$ |
| $f'(g(x)) = (f \circ g)'(x)$ | $(f \circ g)'(x) = f'(g(x)) \cdot g'(x)$ |

### 3.3 Intégrale

- $\int f \cdot g = (\int f) \cdot (\int g)$ : **faux**, l'intégrale n'est pas multiplicative
- $\int \frac{f'}{g}$ ne se simplifie pas seul ; en revanche $\int \frac{f'}{f} = \ln |f|$
- Ne pas oublier la **constante d'intégration** dans les primitives indéfinies
- Ne pas oublier le **dx** (vérifier que ce qu'on écrit a un sens)

### 3.4 Convergence

| Erreur | Précision |
|---|---|
| « $u_n$ converge car $u_{n+1} - u_n \to 0$ » | **Faux** : pour $u_n = \ln n$, on a $u_{n+1} - u_n = \ln(1 + 1/n) \to 0$, mais $u_n \to +\infty$ |
| « $\sum u_n$ converge ssi $u_n \to 0$ » | $u_n \to 0$ est **nécessaire** mais **pas suffisant** ($\sum 1/n$ diverge) |
| Inverser limite et intégrale sans précaution | Nécessite **convergence dominée** ou **uniforme** |
| Dériver une série terme à terme | Nécessite **convergence uniforme de la série dérivée** |

## 4. Erreurs en algèbre linéaire

### 4.1 Confondre les objets

- $\dim(\ker f) + \dim(\text{Im } f) = \dim E$ (théorème du rang) — pas $\dim F$
- Une **matrice** n'est **pas** une application linéaire ; c'est sa **représentation dans une base donnée**
- $A B \neq B A$ en général — l'algèbre des matrices n'est **pas commutative**

### 4.2 Inversibilité

| Erreur | Réalité |
|---|---|
| $(A + B)^{-1} = A^{-1} + B^{-1}$ | **Faux** en général |
| $(AB)^{-1} = A^{-1} B^{-1}$ | **Faux** : c'est $(AB)^{-1} = B^{-1} A^{-1}$ |
| $\det(A + B) = \det A + \det B$ | **Faux** (le déterminant n'est pas linéaire, mais multi-linéaire en colonnes) |
| $\det(AB) = \det A + \det B$ | C'est $\det A \cdot \det B$ |
| $\det(\lambda A) = \lambda \det A$ | C'est $\lambda^n \det A$ en dimension $n$ |

### 4.3 Valeurs propres et diagonalisation

- Une matrice avec polynôme caractéristique scindé n'est pas toujours diagonalisable (il faut **simplicité des racines** ou que les dimensions des sous-espaces propres égalent les multiplicités)
- Diagonalisable sur $\mathbb{C}$ n'implique pas diagonalisable sur $\mathbb{R}$ (matrice de rotation 2D)
- $0$ valeur propre $\Leftrightarrow$ matrice non inversible

## 5. Erreurs en arithmétique

| Erreur | Correction |
|---|---|
| $\gcd(a, b) \cdot \text{lcm}(a, b) = a + b$ | C'est $a \cdot b$ |
| $a \equiv b \pmod n$ et $c \equiv d \pmod n$ ⇒ $a/c \equiv b/d$ | **Faux** : la division modulaire exige l'inversibilité |
| $a \mid bc$ ⇒ $a \mid b$ ou $a \mid c$ | Vrai **seulement si $a$ premier** (lemme d'Euclide) |
| $a \mid b$ et $a \mid c$ ⇒ $a \mid \gcd(b, c)$ | OK |
| $\gcd(a, b) = 1$ et $a \mid bc$ ⇒ $a \mid c$ | OK (Gauss) |

## 6. Erreurs en probabilités

### 6.1 Indépendance vs incompatibilité

- **Incompatibles** : $A \cap B = \varnothing$ (les deux ne peuvent se réaliser ensemble)
- **Indépendants** : $P(A \cap B) = P(A) P(B)$ (la connaissance de l'un n'influe pas sur l'autre)
- Deux événements de probabilité non nulle ne peuvent **pas** être à la fois incompatibles et indépendants

### 6.2 Variance et indépendance

- $E(X + Y) = E(X) + E(Y)$ **toujours** (linéarité)
- $V(X + Y) = V(X) + V(Y)$ **seulement si** $X$ et $Y$ indépendantes
- $V(aX) = a^2 V(X)$ (pas $aV(X)$)

### 6.3 Bayes et taux de base

> [!example] Le piège du dépistage
> Une maladie touche 1 % de la population. Un test a 99 % de fiabilité (sensibilité et spécificité). Si tu es testé positif, quelle est la probabilité que tu sois malade ?
> 
> Intuition courante : ~99 %. **Réalité** : ~50 %, par Bayes.
> 
> $$P(M \mid +) = \frac{P(+ \mid M) P(M)}{P(+)} = \frac{0{,}99 \times 0{,}01}{0{,}99 \times 0{,}01 + 0{,}01 \times 0{,}99} = 0{,}5$$
> 
> *Morale* : ignorer le taux de base (1 %) fait perdre tout le sens.

## 7. Erreurs de récurrence

| Erreur | Correction |
|---|---|
| Oublier l'initialisation | L'hérédité seule ne suffit pas |
| Faire l'hérédité pour un seul $n$ | Doit marcher pour **tout** $n \geq n_0$ |
| Confondre $P(n)$ avec « le résultat pour $n$ » | Bien écrire $P(n)$ comme une proposition |
| Récurrence forte sans initialisation suffisante | Si l'hérédité utilise $P(0), \dots, P(n)$, il faut initialiser tous ces cas |
| Récurrence sur $n$ alors que $P(n)$ dépend continûment de $x$ | La récurrence opère sur $\mathbb{N}$, pas $\mathbb{R}$ |

## 8. Pièges méta

### 8.1 Cas particulier $\neq$ démonstration

Vérifier un résultat pour $n = 1, 2, 3$ ne le démontre pas — c'est une *plausibilité*, pas une preuve. La conjecture de Pólya tient pour $n < 906\,150\,257$, puis casse.

### 8.2 « Sans perte de généralité »

Cette phrase n'est valable que si on peut **vraiment** réduire au cas étudié par symétrie ou changement de variable. Vérifier que la généralité n'est pas perdue !

### 8.3 Hypothèses oubliées

Lire l'énoncé **lentement** et noter chaque hypothèse. Une démonstration qui n'utilise pas toutes les hypothèses est suspecte (soit elles sont superflues, soit on a sauté un point).

### 8.4 Conclusion qui dépasse les hypothèses

Si l'énoncé demande une propriété sur $\mathbb{R}^+$, ne pas la prouver sur $\mathbb{R}$ tout entier sauf si c'est plus facile et automatique.

### 8.5 Notation incohérente

- Réutiliser un nom de variable déjà pris (le $n$ de l'énoncé et un autre $n$ d'indice)
- Mélanger $f$ et $f(x)$ (la fonction et sa valeur en un point)
- Confondre $f(x_n)$ et $(f(x))_n$

## 9. Erreurs de présentation

| Erreur | Conseil |
|---|---|
| Page noire d'écritures non hiérarchisées | Aérer, souligner les résultats clés, encadrer la conclusion |
| Conclusion implicite | Toujours finir par « par conséquent… » ou un encadré |
| Hypothèses non rappelées | Au début de la résolution, écrire « Soit $f$ une fonction continue… » |
| Calculs intermédiaires raturés sur la copie | Faire les calculs au brouillon, recopier les étapes propres |
| Pas de dessin en géométrie / analyse | Toujours faire un schéma quand c'est possible |

## Comment auto-corriger une copie

1. **Relire** une fois pour la cohérence logique (les implications sont-elles correctes ?)
2. **Relire** une fois pour la cohérence des hypothèses (chaque hypothèse est-elle utilisée ?)
3. **Relire** une fois pour les calculs (refaire mentalement les passages cruciaux)
4. **Vérifier** sur un cas simple (n = 1, dimension 2) si possible
5. **Vérifier la conclusion** : répond-elle exactement à la question ?

Voir [[Méthodes de Démonstration]] et [[Comment Montrer Que]] pour les bonnes pratiques.
