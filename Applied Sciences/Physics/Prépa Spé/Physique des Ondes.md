---
title: "Physique des Ondes"
domain: "Applied Sciences"
subdomain: "Physics > Prépa Spé"
tags: [sciences-appliquées, physique, ondes, prépa]
date: "2026-06-21"
---

# Physique des Ondes

Cette note traite les ondes de façon **générale et unifiée** : équation de propagation, ondes stationnaires, dispersion, paquets d'ondes. Le même formalisme décrit cordes, son, lumière ([[Ondes Électromagnétiques]]) et fonctions d'onde quantiques ([[Mécanique Quantique]]). Prérequis : [[Équations Différentielles]], [[Séries de Fourier]].

## 1. L'équation de d'Alembert

> [!important] Équation d'onde unidimensionnelle
> La plupart des ondes obéissent à l'équation de d'Alembert :
> $$\frac{\partial^2 s}{\partial x^2} = \frac{1}{c^2}\frac{\partial^2 s}{\partial t^2}$$
> où $c$ est la **célérité**. Ses solutions sont la superposition d'une onde se propageant vers les $x$ croissants et d'une vers les $x$ décroissants :
> $$s(x, t) = f\!\left(t - \frac{x}{c}\right) + g\!\left(t + \frac{x}{c}\right)$$

| Onde | Célérité $c$ |
|------|--------------|
| Corde de masse linéique $\mu$, tension $T$ | $\sqrt{\dfrac{T}{\mu}}$ |
| Son dans un gaz | $\sqrt{\dfrac{\gamma R T}{M}}$ |
| Onde EM dans le vide | $\dfrac{1}{\sqrt{\varepsilon_0\mu_0}}$ |

## 2. Ondes planes progressives harmoniques

> [!important] Notation et relation de dispersion
> $$s(x, t) = A\cos(\omega t - kx)$$
> avec $\omega$ pulsation, $k$ nombre d'onde. La **relation de dispersion** relie $\omega$ et $k$ ; pour d'Alembert : $\omega = ck$.
> - Vitesse de phase : $v_\varphi = \dfrac{\omega}{k}$.
> - Vitesse de groupe : $v_g = \dfrac{\mathrm d\omega}{\mathrm dk}$ (vitesse de l'énergie / de l'information).

> [!important] Milieu dispersif
> Si $v_\varphi$ dépend de $\omega$, le milieu est **dispersif** : un paquet d'ondes s'y déforme et $v_g \neq v_\varphi$. Exemple : la lumière dans le verre (d'où la décomposition par un prisme).

## 3. Ondes stationnaires

> [!important] Formation d'une onde stationnaire
> La superposition de deux ondes identiques se propageant en sens inverses (onde + sa réflexion) donne une **onde stationnaire** :
> $$s(x, t) = 2A\cos(kx)\cos(\omega t)$$
> L'onde n'avance plus : chaque point oscille sur place avec une amplitude $2A\cos(kx)$ fixée par sa position.

> [!important] Nœuds, ventres et modes propres
> - **Nœuds** : points immobiles ($\cos kx = 0$).
> - **Ventres** : amplitude maximale.
> - Une corde fixée aux deux bouts (longueur $L$) ne vibre qu'à des **fréquences propres** quantifiées :
> $$f_n = n\,\frac{c}{2L}, \quad n \in \mathbb N^*$$
> C'est l'origine des notes d'un instrument à cordes : fondamentale ($n=1$) et harmoniques.

### Visualisation animée (Manim)

> [!note] Ce que montre l'animation
> Une corde fixée à ses deux extrémités vibre selon ses premiers modes propres ($n = 1, 2, 3$). On voit les **nœuds** (points immobiles) et les **ventres** (oscillation maximale). Le motif n'avance pas : c'est une onde stationnaire. On *voit* pourquoi seules certaines fréquences (harmoniques) sont possibles sur une corde de longueur fixée.

```manim
# Rendu : manimgl onde_stationnaire.py OndeStationnaire
from manimlib import *


class OndeStationnaire(Scene):
    def construct(self):
        L = 10.0
        x0 = -5.0
        axes_y = 1.5

        t = ValueTracker(0.0)
        mode = ValueTracker(1)

        def corde():
            n = int(round(mode.get_value()))
            k = n * PI / L
            w = 2.0 * n
            pts = [np.array([x0 + x, axes_y * np.sin(k * x) * np.cos(w * t.get_value()), 0])
                   for x in np.linspace(0, L, 200)]
            return VMobject().set_points_smoothly(pts).set_color(BLUE)

        c = always_redraw(corde)
        murs = VGroup(Dot(np.array([x0, 0, 0]), color=WHITE),
                      Dot(np.array([x0 + L, 0, 0]), color=WHITE))
        self.add(c, murs)

        label = always_redraw(lambda: Tex(
            f"n = {int(round(mode.get_value()))}").to_edge(UP).set_backstroke())
        self.add(label)

        for n in (1, 2, 3):
            self.play(mode.animate.set_value(n), run_time=0.5)
            self.play(t.animate.increment_value(2 * PI), run_time=3, rate_func=linear)
        self.wait()
```

## 4. Le paquet d'ondes

> [!important] Localiser une onde
> Une onde monochromatique pure est infiniment étendue. Pour localiser un signal, on **superpose** des ondes de fréquences voisines : c'est un **paquet d'ondes**, dont la largeur spatiale $\Delta x$ et la largeur spectrale $\Delta k$ vérifient :
> $$\Delta x\,\Delta k \gtrsim 1$$
> Plus le paquet est étroit dans l'espace, plus il est large en fréquences. C'est l'analogue classique de l'inégalité de Heisenberg (voir [[Mécanique Quantique]]) et un résultat de l'analyse de [[Séries de Fourier|Fourier]].

## 5. Effet Doppler

> [!important] Décalage de fréquence
> Le mouvement relatif source-observateur décale la fréquence perçue : plus élevée en rapprochement, plus basse en éloignement. Pour une source sonore de vitesse $v_s$ (faible devant $c_{\text{son}}$) :
> $$f' \approx f\left(1 \pm \frac{v_s}{c_{\text{son}}}\right)$$
> Applications : radar, débitmétrie sanguine, décalage vers le rouge des galaxies ([[Astrophysique et Cosmologie]]).

## 6. Exercices types corrigés

### Exercice 1 : fréquence fondamentale d'une corde

**Énoncé** : Une corde de guitare de longueur $L = 65$ cm, de masse linéique $\mu = 5{,}0$ g·m⁻¹, est tendue à $T = 80$ N. Quelle est sa fréquence fondamentale ?

> [!example] Correction
> Célérité : $c = \sqrt{\dfrac{T}{\mu}} = \sqrt{\dfrac{80}{5{,}0\times10^{-3}}} = \sqrt{16\,000} = 126{,}5$ m·s⁻¹.
> $$f_1 = \frac{c}{2L} = \frac{126{,}5}{2 \times 0{,}65} \approx 97 \text{ Hz}$$

### Exercice 2 : vitesse de phase vs groupe

**Énoncé** : Dans un milieu, la relation de dispersion est $\omega = a k^2$. Comparer vitesse de phase et vitesse de groupe.

> [!example] Correction
> $$v_\varphi = \frac{\omega}{k} = ak, \qquad v_g = \frac{\mathrm d\omega}{\mathrm dk} = 2ak = 2v_\varphi$$
> Le milieu est dispersif ; l'énergie va deux fois plus vite que les crêtes.

### Exercice 3 : harmoniques

**Énoncé** : Une corde émet un fondamental à $200$ Hz. Quelles sont les fréquences des deux harmoniques suivantes ?

> [!example] Correction
> $f_n = n f_1$ : $f_2 = 400$ Hz, $f_3 = 600$ Hz. Le timbre d'un instrument vient du **mélange** de ces harmoniques (analyse de Fourier).

## 7. À retenir

> [!tip] À retenir
> - **d'Alembert** : $\partial_x^2 s = \dfrac{1}{c^2}\partial_t^2 s$ ; solutions = ondes vers $\pm x$.
> - **Dispersion** : $v_\varphi = \omega/k$, $v_g = \mathrm d\omega/\mathrm dk$ ; égales seulement en milieu non dispersif.
> - **Ondes stationnaires** : nœuds et ventres ; modes propres quantifiés $f_n = n\,c/2L$ (instruments).
> - **Paquet d'ondes** : $\Delta x\,\Delta k \gtrsim 1$ (Fourier) — préfigure Heisenberg.
> - **Doppler** : la fréquence perçue dépend du mouvement relatif.

*Voir aussi* : [[Ondes Mécaniques et Son]] | [[Ondes Électromagnétiques]] | [[Mécanique Quantique]] | [[Séries de Fourier]] | [[Oscillateurs]]
