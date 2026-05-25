---
title: "Théorie des Nombres"
domain: "Applied Sciences"
subdomain: "Mathematics > Approfondissements"
tags: [sciences-appliquées, mathématiques, théorie-des-nombres, premiers, rsa, fermat, riemann]
date: "2026-05-20"
---

# Théorie des Nombres

La théorie des nombres est l'étude des entiers naturels — l'objet mathématique le plus simple en apparence, le plus profond en réalité. Pythagore et Diophante posaient déjà ses questions ; Fermat, Euler, Gauss, Riemann l'ont construite ; et c'est elle qui sécurise aujourd'hui ton compte bancaire. *« La théorie des nombres est la reine des mathématiques »* (Gauss).

> [!abstract] Pré-requis
> Cette note prolonge [[Arithmétique]] (Math Sup) avec des résultats classiques et appliqués : RSA, théorèmes de Fermat, fonction zêta, conjectures célèbres.

## 1. Nombres premiers — les briques fondamentales

### 1.1 Définition et théorème fondamental

> [!important] Théorème fondamental de l'arithmétique
> Tout entier $n \geq 2$ s'écrit de manière **unique** (à l'ordre près) comme produit de nombres premiers :
> $$n = p_1^{\alpha_1} p_2^{\alpha_2} \cdots p_k^{\alpha_k}$$

Les premiers sont aux entiers ce que les atomes sont aux molécules.

### 1.2 Infinité des nombres premiers (Euclide, ~300 av. J.-C.)

> [!quote] Preuve par l'absurde — Euclide
> Supposons qu'il n'y ait qu'un nombre fini de premiers : $p_1, p_2, \dots, p_n$. Considérons $N = p_1 p_2 \cdots p_n + 1$.
> - Soit $N$ est premier (et plus grand que tous les $p_i$) — contradiction.
> - Soit $N$ admet un diviseur premier $p$. Or $p$ doit être l'un des $p_i$, donc $p \mid p_1 \cdots p_n$. Comme $p \mid N$, on a $p \mid (N - p_1 \cdots p_n) = 1$, absurde.

Une des plus belles démonstrations de toute l'histoire mathématique — limpide en 5 lignes.

### 1.3 Distribution des premiers

Combien y a-t-il de premiers $\leq x$ ? On note ce nombre $\pi(x)$.

| $x$ | $\pi(x)$ | $x / \ln x$ |
|---|---|---|
| 100 | 25 | 21,7 |
| 1 000 | 168 | 144,8 |
| 10⁶ | 78 498 | 72 382 |
| 10⁹ | 50 847 534 | 48 254 942 |

> [!important] Théorème des nombres premiers (Hadamard et de la Vallée Poussin, 1896)
> $$\pi(x) \sim \frac{x}{\ln x} \quad \text{quand } x \to \infty$$

Les premiers se raréfient logarithmiquement. Démontré indépendamment en 1896 par les deux mathématiciens, après un siècle de conjectures.

### 1.4 Test de primalité

| Méthode | Complexité | Quand l'utiliser |
|---|---|---|
| **Crible d'Ératosthène** | $O(n \log \log n)$ | Liste tous les premiers ≤ $n$ |
| **Test de Fermat** | $O(\log^3 n)$ | Probabiliste, faux positifs (Carmichael) |
| **Miller-Rabin** | $O(k \log^3 n)$ | Probabiliste, RSA en pratique |
| **AKS (Agrawal-Kayal-Saxena, 2002)** | $O(\log^{6+\varepsilon} n)$ | Déterministe — exploit théorique majeur |

## 2. Congruences et modulos

> [!abstract] Définition
> $a \equiv b \pmod{n}$ signifie que $n \mid (a - b)$.

L'arithmétique modulo $n$ est compatible avec les opérations :
- $a \equiv b$ et $c \equiv d$ $\Rightarrow$ $a+c \equiv b+d$ et $ac \equiv bd$

### 2.1 Petit théorème de Fermat (1640)

> [!important] Petit théorème de Fermat
> Soit $p$ premier. Pour tout entier $a$ non multiple de $p$ :
> $$a^{p-1} \equiv 1 \pmod{p}$$
>
> Forme équivalente : $a^p \equiv a \pmod{p}$ pour tout $a$.

**Application** : test de primalité probabiliste (si $a^{n-1} \not\equiv 1 \pmod n$, alors $n$ n'est pas premier).

### 2.2 Théorème d'Euler — généralisation

> [!important] Théorème d'Euler
> Si $\gcd(a, n) = 1$ :
> $$a^{\varphi(n)} \equiv 1 \pmod{n}$$
>
> où $\varphi(n)$ est l'**indicatrice d'Euler** = nombre d'entiers entre 1 et $n$ premiers avec $n$.

**Calcul de $\varphi(n)$** : pour $n = p_1^{\alpha_1} \cdots p_k^{\alpha_k}$,
$$\varphi(n) = n \prod_{i=1}^k \left(1 - \frac{1}{p_i}\right)$$

### 2.3 Théorème des restes chinois (CRT)

> [!important] Théorème des restes chinois
> Si $n_1, n_2, \dots, n_k$ sont **premiers entre eux deux à deux**, le système :
> $$\begin{cases} x \equiv a_1 \pmod{n_1} \\ \vdots \\ x \equiv a_k \pmod{n_k} \end{cases}$$
> admet une **unique solution modulo** $N = n_1 n_2 \cdots n_k$.

Découvert au IIIe siècle par Sun Zi (« Sunzi Suanjing »). Aujourd'hui utilisé pour accélérer RSA (calculs séparés mod $p$ et mod $q$).

## 3. RSA — la cryptographie asymétrique

### 3.1 Le principe (Rivest, Shamir, Adleman, 1977)

Première application massive de la théorie des nombres au monde réel.

**Idée** : il est facile de multiplier deux grands nombres premiers, mais essentiellement impossible de factoriser le produit en un temps raisonnable. Cette asymétrie permet une cryptographie où la clé publique peut être distribuée librement.

### 3.2 Génération des clés

1. Choisir deux grands premiers $p$ et $q$ (typiquement 1024 bits chacun)
2. Calculer $n = pq$ et $\varphi(n) = (p-1)(q-1)$
3. Choisir $e$ premier avec $\varphi(n)$ (souvent $e = 65537 = 2^{16}+1$)
4. Calculer $d$ tel que $ed \equiv 1 \pmod{\varphi(n)}$ (par Euclide étendu)

- **Clé publique** : $(n, e)$
- **Clé privée** : $(n, d)$

### 3.3 Chiffrement / déchiffrement

Pour chiffrer un message $m$ ($0 < m < n$) :
$$c = m^e \mod n$$

Pour déchiffrer :
$$m = c^d \mod n$$

**Pourquoi ça marche** ? Par Fermat-Euler :
$$c^d = m^{ed} = m^{1 + k\varphi(n)} = m \cdot (m^{\varphi(n)})^k \equiv m \cdot 1^k \equiv m \pmod n$$

### 3.4 Sécurité

La sécurité repose entièrement sur la difficulté de **factoriser $n$**. Avec $n$ de 2048 bits, c'est aujourd'hui infaisable classiquement (~10²⁰ années CPU).

> [!warning] L'ombre quantique
> L'algorithme de **Shor** (1994) factorise en temps polynomial sur un ordinateur quantique. Un ordinateur quantique tolérant aux fautes suffisamment grand (~4 000 qubits logiques) casserait RSA-2048. D'où la course à la **cryptographie post-quantique** (lattices, codes, isogénies).

## 4. La fonction zêta de Riemann

> [!abstract] Définition
> $$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s}$$
>
> Définie pour $\text{Re}(s) > 1$, prolongée analytiquement à $\mathbb{C} \setminus \{1\}$.

### 4.1 Produit eulérien (1737)

$$\zeta(s) = \prod_{p \text{ premier}} \frac{1}{1 - p^{-s}}$$

Découverte d'Euler — **la fonction zêta contient toute l'information sur les premiers**. C'est l'identité fondatrice de la théorie analytique des nombres.

### 4.2 Valeurs remarquables

| $s$ | $\zeta(s)$ | Découvert par |
|---|---|---|
| $2$ | $\pi^2 / 6$ | Euler (1735) — problème de Bâle |
| $4$ | $\pi^4 / 90$ | Euler |
| $2k$ ($k$ entier) | $\frac{(-1)^{k+1}(2\pi)^{2k} B_{2k}}{2(2k)!}$ | Euler (nombres de Bernoulli) |
| $-1$ | $-1/12$ | Prolongement analytique (« $1+2+3+\cdots = -1/12$ ») |
| $3$ | $\zeta(3) \approx 1{,}20206$ | Apéry (1978, irrationalité) |

### 4.3 L'hypothèse de Riemann (1859)

> [!quote] Hypothèse de Riemann
> Tous les zéros non triviaux de $\zeta(s)$ ont pour partie réelle $\text{Re}(s) = 1/2$.

**Pourquoi c'est important** : la position de ces zéros contrôle la précision avec laquelle on peut estimer $\pi(x)$. Si l'hypothèse est vraie, on connaît la distribution des premiers à $O(\sqrt{x} \log x)$ près — sinon, à beaucoup moins.

- Un des [[Applications des Mathématiques#Problèmes du millénaire|7 problèmes du millénaire]] (prime : 1 M$)
- Vérifiée numériquement pour les premiers ~10 trillions de zéros
- Toujours ouverte depuis 1859 — peut-être le plus célèbre problème non résolu des mathématiques

## 5. Équations diophantiennes

Équations à coefficients entiers dont on cherche des solutions entières.

### 5.1 Pythagore et triplets

$x^2 + y^2 = z^2$ admet une infinité de solutions (triplets pythagoriciens) :
- $(3, 4, 5),\; (5, 12, 13),\; (8, 15, 17),\dots$
- Paramétrage complet : $x = m^2 - n^2,\; y = 2mn,\; z = m^2 + n^2$

### 5.2 Le grand théorème de Fermat (1637-1995)

> [!quote] Fermat (note en marge des Arithmétiques de Diophante)
> Pour $n \geq 3$, l'équation $x^n + y^n = z^n$ n'admet aucune solution entière non triviale.
>
> « J'ai trouvé une démonstration véritablement merveilleuse, mais cette marge est trop étroite pour la contenir. »

Resté ouvert pendant **358 ans**. Démontré par **Andrew Wiles** en 1994-1995 (avec Richard Taylor), via la modularité des courbes elliptiques (conjecture de Taniyama-Shimura-Weil) — la « démonstration véritablement merveilleuse » de Fermat n'a jamais été retrouvée et était probablement erronée.

### 5.3 Équations de Pell

$x^2 - D y^2 = 1$ — étudiées par les mathématiciens indiens (Brahmagupta, VIIe siècle), résolues par Lagrange au XVIIIe via les fractions continues.

## 6. Conjectures célèbres ouvertes

| Conjecture | Énoncé | Statut |
|---|---|---|
| **Riemann** | Zéros non triviaux de $\zeta$ sur $\text{Re} = 1/2$ | Ouverte (Clay, 1 M$) |
| **Goldbach (1742)** | Tout entier pair $\geq 4$ est somme de deux premiers | Vérifiée jusqu'à $4 \cdot 10^{18}$, ouverte |
| **Premiers jumeaux** | Il existe une infinité de paires $(p, p+2)$ premières | Ouverte (résultat de Zhang 2013 : infinité de paires à écart ≤ 7·10⁷, descendu à 246) |
| **Collatz / Syracuse** | La suite $n \to n/2$ ou $3n+1$ atteint toujours 1 | Ouverte, vérifiée jusqu'à $2^{68}$ |
| **abc** | Conjecture sur les triplets $(a, b, c)$ avec $a + b = c$ — implique beaucoup de résultats | Démonstration controversée de Mochizuki (2012, non acceptée par la communauté) |

## 7. Théorèmes spectaculaires démontrés récemment

- **Théorème de Fermat** (Wiles, 1995)
- **Conjecture de Poincaré** (Perelman, 2003) — 1 M$ refusé
- **Théorème de Green-Tao** (2004) : il existe des progressions arithmétiques arbitrairement longues dans les premiers
- **Théorème de Helfgott** (2013) : conjecture faible de Goldbach (tout impair > 5 est somme de 3 premiers)
- **Théorème de Maynard-Tao** (2014) : écarts bornés entre premiers consécutifs

## 8. Pourquoi c'est important aujourd'hui

| Domaine | Application |
|---|---|
| **Cryptographie** | RSA, ECC, Diffie-Hellman, signatures |
| **Codes correcteurs** | Codes BCH, Reed-Solomon (corps finis) |
| **Algorithmique** | Hash, génération pseudo-aléatoire, randomisation |
| **Calcul formel** | Algèbre symbolique, factorisation polynomiale |
| **Informatique théorique** | Complexité, P vs NP |
| **Physique** | Mécanique statistique (fonctions zêta de variétés), théorie des cordes |

Une grande partie des mathématiques « pures » de la théorie des nombres est devenue cruciale en pratique au XXe siècle. Voir [[Arithmétique]] pour les bases (Bézout, Gauss, congruences) et [[Applications des Mathématiques]] pour la vue d'ensemble des applications.
