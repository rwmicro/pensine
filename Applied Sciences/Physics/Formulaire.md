---
title: "Formulaire de Physique"
domain: "Applied Sciences"
subdomain: "Physics"
tags: [sciences-appliquées, physique, formulaire]
date: "2026-06-21"
---

# Formulaire de Physique

Toutes les formules clés du lycée à la prépa, regroupées par domaine. Pour le détail et les démonstrations, voir la note du chapitre concerné.

## 1. Mécanique

### 1.1 Cinématique

$$\vec{v} = \frac{\mathrm{d}\vec{r}}{\mathrm{d}t}, \qquad \vec{a} = \frac{\mathrm{d}\vec{v}}{\mathrm{d}t} = \frac{\mathrm{d}^2\vec{r}}{\mathrm{d}t^2}$$

Mouvement uniformément accéléré (1D) :
$$v(t) = v_0 + at, \qquad x(t) = x_0 + v_0 t + \tfrac{1}{2}at^2, \qquad v^2 = v_0^2 + 2a(x - x_0)$$

Mouvement circulaire uniforme : $v = R\omega$, accélération centripète $a_n = \dfrac{v^2}{R} = R\omega^2$.

### 1.2 Dynamique (lois de Newton)

$$\sum \vec{F} = m\vec{a} \quad \text{(2}^\text{e}\text{ loi)}, \qquad \vec{F}_{A/B} = -\vec{F}_{B/A} \quad \text{(3}^\text{e}\text{ loi)}$$

Quantité de mouvement : $\vec{p} = m\vec{v}$, et $\dfrac{\mathrm{d}\vec{p}}{\mathrm{d}t} = \sum \vec{F}$.

### 1.3 Énergie

$$E_c = \tfrac{1}{2}mv^2, \qquad W_{AB}(\vec{F}) = \int_A^B \vec{F}\cdot \mathrm{d}\vec{r}$$

Énergie potentielle de pesanteur : $E_p = mgz$. Élastique : $E_p = \tfrac{1}{2}kx^2$.

Théorème de l'énergie cinétique : $\Delta E_c = \sum W(\vec{F})$.

Énergie mécanique : $E_m = E_c + E_p$, conservée si forces conservatives.

### 1.4 Moment cinétique

$$\vec{L}_O = \vec{OM}\wedge m\vec{v}, \qquad \frac{\mathrm{d}\vec{L}_O}{\mathrm{d}t} = \vec{\mathcal{M}}_O(\vec{F})$$

### 1.5 Gravitation

$$\vec{F} = -\frac{G m_1 m_2}{r^2}\,\vec{u}_r, \qquad E_p = -\frac{G m_1 m_2}{r}$$

Période orbitale (3e loi de Kepler) : $\dfrac{T^2}{a^3} = \dfrac{4\pi^2}{G M}$.

## 2. Oscillateurs

Oscillateur harmonique : $\ddot{x} + \omega_0^2 x = 0$, solution $x = A\cos(\omega_0 t + \varphi)$.

Pulsation propre : ressort $\omega_0 = \sqrt{\dfrac{k}{m}}$ ; pendule $\omega_0 = \sqrt{\dfrac{g}{\ell}}$.

Période : $T = \dfrac{2\pi}{\omega_0}$.

Amorti : $\ddot{x} + \dfrac{\omega_0}{Q}\dot{x} + \omega_0^2 x = 0$ (facteur de qualité $Q$).

## 3. Thermodynamique

$$PV = nRT \quad \text{(gaz parfait)}, \qquad \Delta U = Q + W \quad \text{(1}^\text{er}\text{ principe)}$$

> [!note] Convention de signe
> Ici $W$ et $Q$ sont comptés **reçus** par le système (convention thermodynamique moderne). Attention : certaines références notent $\Delta U = Q - W$ avec $W$ fourni par le système.

$$W = -\int P\,\mathrm{d}V, \qquad Q = mc\,\Delta T, \qquad \Delta S \geq \frac{Q}{T} \quad \text{(2}^\text{e}\text{ principe)}$$

Entropie statistique : $S = k_B \ln \Omega$.

Rendement de Carnot : $\eta = 1 - \dfrac{T_f}{T_c}$.

Loi de Laplace (adiabatique réversible, GP) : $PV^\gamma = \text{cste}$.

## 4. Électricité et électromagnétisme

### 4.1 Électrocinétique

$$U = RI, \qquad P = UI = RI^2, \qquad q = C\,u_C, \qquad u_L = L\frac{\mathrm{d}i}{\mathrm{d}t}$$

Lois de Kirchhoff : $\sum i_{\text{entrant}} = \sum i_{\text{sortant}}$ (nœuds), $\sum u = 0$ (mailles).

Circuit RC : $\tau = RC$. Circuit RL : $\tau = \dfrac{L}{R}$. RLC : $\omega_0 = \dfrac{1}{\sqrt{LC}}$.

Impédances (RSF) : $\underline{Z}_R = R$, $\underline{Z}_C = \dfrac{1}{jC\omega}$, $\underline{Z}_L = jL\omega$.

### 4.2 Électrostatique et magnétostatique

$$\vec{E} = \frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}\,\vec{u}_r, \qquad \vec{F} = q\vec{E} + q\vec{v}\wedge\vec{B} \quad \text{(Lorentz)}$$

Potentiel : $V = \dfrac{q}{4\pi\varepsilon_0 r}$, et $\vec{E} = -\vec{\nabla} V$.

Théorème de Gauss : $\displaystyle\oiint \vec{E}\cdot \mathrm{d}\vec{S} = \frac{Q_{\text{int}}}{\varepsilon_0}$.

### 4.3 Équations de Maxwell (vide)

$$\vec{\nabla}\cdot\vec{E} = \frac{\rho}{\varepsilon_0}, \qquad \vec{\nabla}\cdot\vec{B} = 0$$
$$\vec{\nabla}\wedge\vec{E} = -\frac{\partial \vec{B}}{\partial t}, \qquad \vec{\nabla}\wedge\vec{B} = \mu_0\vec{j} + \mu_0\varepsilon_0\frac{\partial \vec{E}}{\partial t}$$

Induction : $e = -\dfrac{\mathrm{d}\Phi}{\mathrm{d}t}$ (loi de Faraday).

## 5. Ondes et optique

Relation fondamentale : $v = \lambda f = \dfrac{\lambda}{T}$.

Équation de d'Alembert : $\dfrac{\partial^2 s}{\partial x^2} = \dfrac{1}{c^2}\dfrac{\partial^2 s}{\partial t^2}$.

Snell-Descartes : $n_1 \sin i_1 = n_2 \sin i_2$, indice $n = \dfrac{c}{v}$.

Lentilles minces : $\dfrac{1}{\overline{OA'}} - \dfrac{1}{\overline{OA}} = \dfrac{1}{f'}$, vergence $V = \dfrac{1}{f'}$ (dioptries).

Fentes de Young : interfrange $i = \dfrac{\lambda D}{a}$.

Énergie du photon : $E = h\nu = \dfrac{hc}{\lambda}$.

## 6. Relativité et quantique

Facteur de Lorentz : $\gamma = \dfrac{1}{\sqrt{1 - v^2/c^2}}$.

Dilatation du temps : $\Delta t = \gamma\,\Delta t_0$. Énergie de masse : $E = \gamma mc^2$, au repos $E_0 = mc^2$.

De Broglie : $\lambda = \dfrac{h}{p}$. Heisenberg : $\Delta x \cdot \Delta p \geq \dfrac{\hbar}{2}$.

Schrödinger : $i\hbar\dfrac{\partial \psi}{\partial t} = \hat{H}\psi$. Énergie : $E = h\nu$.

## 7. À retenir

> [!tip] Comment utiliser ce formulaire
> Une formule n'a de sens que si l'on connaît **son domaine de validité** (gaz parfait, régime permanent, forces conservatives, faibles vitesses…). Vérifier systématiquement l'**homogénéité** (voir [[Constantes et Unités]]) avant d'appliquer.

*Voir aussi* : [[Constantes et Unités]] | [[Méthodes de Résolution]] | [[Index]]
