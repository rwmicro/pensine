---
title: "Formulaire de Mathématiques"
domain: "Applied Sciences"
subdomain: "Mathematics"
tags: [sciences-appliquées, mathématiques]
date: "2026-02-16"
---

# Formulaire de Mathématiques

Toutes les formules essentielles en une page. Pour les détails et démonstrations, suivre les liens vers les notes complètes.


## Identités remarquables

$$\begin{aligned}
(a+b)^2 &= a^2 + 2ab + b^2 \\
(a-b)^2 &= a^2 - 2ab + b^2 \\
(a+b)(a-b) &= a^2 - b^2 \\
(a+b)^3 &= a^3 + 3a^2b + 3ab^2 + b^3 \\
a^3 - b^3 &= (a-b)(a^2 + ab + b^2) \\
a^n - b^n &= (a-b)(a^{n-1} + a^{n-2}b + \cdots + b^{n-1})
\end{aligned}$$

Voir [[Calcul Algébrique]]


## Trigonométrie

### Valeurs remarquables

| $\theta$ | $0$ | $\frac{\pi}{6}$ | $\frac{\pi}{4}$ | $\frac{\pi}{3}$ | $\frac{\pi}{2}$ | $\pi$ |
|---|---|---|---|---|---|---|
| $\cos\theta$ | $1$ | $\frac{\sqrt{3}}{2}$ | $\frac{\sqrt{2}}{2}$ | $\frac{1}{2}$ | $0$ | $-1$ |
| $\sin\theta$ | $0$ | $\frac{1}{2}$ | $\frac{\sqrt{2}}{2}$ | $\frac{\sqrt{3}}{2}$ | $1$ | $0$ |
| $\tan\theta$ | $0$ | $\frac{1}{\sqrt{3}}$ | $1$ | $\sqrt{3}$ | $\nexists$ | $0$ |

### Formules fondamentales

$$\cos^2 x + \sin^2 x = 1$$

**Addition :**
$$\cos(a \pm b) = \cos a \cos b \mp \sin a \sin b$$
$$\sin(a \pm b) = \sin a \cos b \pm \cos a \sin b$$
$$\tan(a \pm b) = \frac{\tan a \pm \tan b}{1 \mp \tan a \tan b}$$

**Duplication :**
$$\cos 2a = \cos^2 a - \sin^2 a = 2\cos^2 a - 1 = 1 - 2\sin^2 a$$
$$\sin 2a = 2\sin a \cos a$$

**Linéarisation :**
$$\cos^2 x = \frac{1 + \cos 2x}{2}, \qquad \sin^2 x = \frac{1 - \cos 2x}{2}$$

**Produit → Somme :**
$$\cos a \cos b = \frac{1}{2}[\cos(a-b) + \cos(a+b)]$$
$$\sin a \sin b = \frac{1}{2}[\cos(a-b) - \cos(a+b)]$$
$$\sin a \cos b = \frac{1}{2}[\sin(a+b) + \sin(a-b)]$$

Voir [[Trigonométrie]]


## Dérivées

| $f(x)$ | $f'(x)$ | Conditions |
|---|---|---|
| $k$ (constante) | $0$ | |
| $x^n$ | $nx^{n-1}$ | $n \in \mathbb{Z}$ |
| $\sqrt{x}$ | $\frac{1}{2\sqrt{x}}$ | $x > 0$ |
| $\frac{1}{x}$ | $-\frac{1}{x^2}$ | $x \neq 0$ |
| $e^x$ | $e^x$ | |
| $\ln x$ | $\frac{1}{x}$ | $x > 0$ |
| $a^x$ | $a^x \ln a$ | $a > 0$ |
| $\sin x$ | $\cos x$ | |
| $\cos x$ | $-\sin x$ | |
| $\tan x$ | $1 + \tan^2 x = \frac{1}{\cos^2 x}$ | |
| $\arcsin x$ | $\frac{1}{\sqrt{1-x^2}}$ | $\|x\| < 1$ |
| $\arccos x$ | $-\frac{1}{\sqrt{1-x^2}}$ | $\|x\| < 1$ |
| $\arctan x$ | $\frac{1}{1+x^2}$ | |
| $\sinh x$ | $\cosh x$ | |
| $\cosh x$ | $\sinh x$ | |

**Opérations :**

| Opération | Formule |
|---|---|
| $(\lambda f + \mu g)'$ | $\lambda f' + \mu g'$ |
| $(fg)'$ | $f'g + fg'$ |
| $(f/g)'$ | $\frac{f'g - fg'}{g^2}$ |
| $(g \circ f)'$ | $(g' \circ f) \cdot f'$ |
| $(f^{-1})'(y)$ | $\frac{1}{f'(f^{-1}(y))}$ |

Voir [[Dérivation]]


## Primitives

| $f(x)$ | $F(x)$ | Conditions |
|---|---|---|
| $x^n$ ($n \neq -1$) | $\frac{x^{n+1}}{n+1}$ | |
| $\frac{1}{x}$ | $\ln\|x\|$ | $x \neq 0$ |
| $e^x$ | $e^x$ | |
| $e^{ax}$ | $\frac{1}{a}e^{ax}$ | |
| $\cos x$ | $\sin x$ | |
| $\sin x$ | $-\cos x$ | |
| $\frac{1}{\cos^2 x}$ | $\tan x$ | |
| $\frac{1}{1+x^2}$ | $\arctan x$ | |
| $\frac{1}{\sqrt{1-x^2}}$ | $\arcsin x$ | |
| $\frac{1}{x^2+a^2}$ | $\frac{1}{a}\arctan\frac{x}{a}$ | $a > 0$ |
| $\frac{1}{\sqrt{x^2+a^2}}$ | $\ln(x + \sqrt{x^2+a^2})$ | |
| $\frac{u'}{u}$ | $\ln\|u\|$ | |
| $u' u^n$ | $\frac{u^{n+1}}{n+1}$ | $n \neq -1$ |
| $u' e^u$ | $e^u$ | |

Voir [[Primitives et Intégrales]]


## Développements limités en 0

$$e^x = 1 + x + \frac{x^2}{2} + \frac{x^3}{6} + \cdots + \frac{x^n}{n!} + o(x^n)$$

$$\sin x = x - \frac{x^3}{6} + \frac{x^5}{120} + \cdots + (-1)^n \frac{x^{2n+1}}{(2n+1)!} + o(x^{2n+2})$$

$$\cos x = 1 - \frac{x^2}{2} + \frac{x^4}{24} + \cdots + (-1)^n \frac{x^{2n}}{(2n)!} + o(x^{2n+1})$$

$$\ln(1+x) = x - \frac{x^2}{2} + \frac{x^3}{3} + \cdots + (-1)^{n-1} \frac{x^n}{n} + o(x^n)$$

$$\frac{1}{1-x} = 1 + x + x^2 + \cdots + x^n + o(x^n)$$

$$\frac{1}{1+x} = 1 - x + x^2 - \cdots + (-1)^n x^n + o(x^n)$$

$$(1+x)^\alpha = 1 + \alpha x + \frac{\alpha(\alpha-1)}{2}x^2 + \cdots + \binom{\alpha}{n}x^n + o(x^n)$$

$$\tan x = x + \frac{x^3}{3} + \frac{2x^5}{15} + o(x^6)$$

$$\arctan x = x - \frac{x^3}{3} + \frac{x^5}{5} + \cdots + (-1)^n \frac{x^{2n+1}}{2n+1} + o(x^{2n+2})$$

Voir [[Développements Limités]]


## Suites

| Type | Terme général | Somme des $n+1$ premiers termes |
|---|---|---|
| Arithmétique ($u_{k+1} = u_k + r$) | $u_n = u_0 + nr$ | $S = (n+1) \cdot \frac{u_0 + u_n}{2}$ |
| Géométrique ($u_{k+1} = q \cdot u_k$) | $u_n = u_0 \cdot q^n$ | $S = u_0 \cdot \frac{1 - q^{n+1}}{1 - q}$ ($q \neq 1$) |

Voir [[Suites]]


## Limites de référence

$$\lim_{x \to 0} \frac{\sin x}{x} = 1 \qquad \lim_{x \to 0} \frac{e^x - 1}{x} = 1 \qquad \lim_{x \to 0} \frac{\ln(1+x)}{x} = 1$$

$$\lim_{x \to +\infty} \frac{e^x}{x^n} = +\infty \qquad \lim_{x \to +\infty} \frac{\ln x}{x^\alpha} = 0 \quad (\alpha > 0)$$

$$\lim_{x \to 0^+} x^\alpha \ln x = 0 \quad (\alpha > 0)$$

Voir [[Limites et Continuité]]


## Combinatoire

$$n! = n \times (n-1) \times \cdots \times 1 \qquad 0! = 1$$

$$\binom{n}{p} = \frac{n!}{p!(n-p)!} \qquad \binom{n}{p} = \binom{n}{n-p} \qquad \binom{n}{p} = \binom{n-1}{p-1} + \binom{n-1}{p}$$

$$(a+b)^n = \sum_{k=0}^{n} \binom{n}{k} a^k b^{n-k}$$

Voir [[Dénombrement]]


## Probabilités

$$P(A \cup B) = P(A) + P(B) - P(A \cap B)$$
$$P(A|B) = \frac{P(A \cap B)}{P(B)} \qquad P(A \cap B) = P(A|B) \cdot P(B)$$

**Formule des probabilités totales :** si $(B_i)$ partition de $\Omega$ :
$$P(A) = \sum_i P(A|B_i) \cdot P(B_i)$$

| Loi | Paramètres | $E(X)$ | $V(X)$ |
|---|---|---|---|
| Bernoulli | $p$ | $p$ | $p(1-p)$ |
| Binomiale | $n, p$ | $np$ | $np(1-p)$ |
| Poisson | $\lambda$ | $\lambda$ | $\lambda$ |
| Géométrique | $p$ | $1/p$ | $(1-p)/p^2$ |
| Uniforme $[a,b]$ | $a, b$ | $\frac{a+b}{2}$ | $\frac{(b-a)^2}{12}$ |
| Exponentielle | $\lambda$ | $1/\lambda$ | $1/\lambda^2$ |
| Normale | $\mu, \sigma^2$ | $\mu$ | $\sigma^2$ |

Voir [[Probabilités]], [[Probabilités Prépa]]


## Séries de référence

| Série | Nature | Somme (si convergente) |
|---|---|---|
| $\sum q^n$ ($\|q\| < 1$) | Converge | $\frac{1}{1-q}$ |
| $\sum \frac{1}{n^\alpha}$ | CV ssi $\alpha > 1$ | $\frac{\pi^2}{6}$ pour $\alpha = 2$ |
| $\sum \frac{1}{n}$ | Diverge | — |
| $\sum \frac{(-1)^n}{n}$ | Converge (Leibniz) | $\ln 2$ |
| $\sum \frac{1}{n!}$ | Converge | $e$ |

Voir [[Suites et Séries Numériques]]


## Intégration — Techniques

**IPP :** $\int_a^b f'g = [fg]_a^b - \int_a^b fg'$

**Changement de variable :** $\int_a^b f(\varphi(t))\varphi'(t) \, dt = \int_{\varphi(a)}^{\varphi(b)} f(u) \, du$

Voir [[Intégration]]


## Algèbre linéaire — Formules clés

**Théorème du rang :** $\dim E = \dim \ker f + \dim \text{Im} f$

**Déterminant :** $\det(AB) = \det A \cdot \det B$, $\det(A^{-1}) = 1/\det A$

**Polynôme caractéristique :** $\chi_A(\lambda) = \det(A - \lambda I)$

**Cayley-Hamilton :** $\chi_A(A) = 0$

Voir [[Algèbre Linéaire]], [[Matrices et Déterminants]], [[Réduction des Endomorphismes]]
