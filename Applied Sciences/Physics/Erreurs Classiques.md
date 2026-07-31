---
title: "Erreurs Classiques en Physique"
domain: "Applied Sciences"
subdomain: "Physics"
tags: [sciences-appliquées, physique, erreurs, pièges]
date: "2026-06-21"
---

# Erreurs Classiques en Physique

Recensement des pièges les plus fréquents, du lycée à la prépa. Les connaître à l'avance évite de les reproduire.

## 1. Mécanique

> [!warning] Confondre force et mouvement
> Un objet peut se déplacer **sans force** dans sa direction de mouvement (1re loi de Newton : mouvement rectiligne uniforme sans force résultante). Une force n'est pas nécessaire pour *maintenir* un mouvement, seulement pour le *modifier*.

> [!warning] La force centrifuge n'existe pas dans un référentiel galiléen
> Dans un mouvement circulaire vu d'un référentiel galiléen, la résultante est **centripète** (dirigée vers le centre). La « force centrifuge » n'apparaît que comme force d'inertie dans un référentiel tournant non galiléen (voir [[Référentiels Non Galiléens]]).

> [!warning] Oublier la réaction du support
> Sur un plan, le poids n'est pas la seule force : la réaction normale $\vec{N}$ équilibre sa composante perpendiculaire. Sur un plan incliné, $N = mg\cos\alpha$, pas $mg$.

> [!warning] Le poids n'est pas la masse
> La masse $m$ (en kg) est intrinsèque ; le poids $P = mg$ (en N) dépend de $g$, donc du lieu. Sur la Lune, la masse est inchangée mais le poids est divisé par 6.

## 2. Énergie

> [!warning] Énergie cinétique et quantité de mouvement
> $E_c = \tfrac{1}{2}mv^2$ (scalaire, en joules) et $\vec{p} = m\vec{v}$ (vecteur) sont deux grandeurs distinctes. Dans un choc, $\vec{p}$ se conserve toujours ; $E_c$ ne se conserve que si le choc est **élastique**.

> [!warning] Signe du travail
> Le travail d'une force est $W = \vec{F}\cdot\vec{d}$ : **négatif** si la force s'oppose au déplacement (frottements, freinage). Oublier ce signe fausse tout bilan énergétique.

## 3. Thermodynamique

> [!warning] Conventions de signe de Q et W
> Selon les conventions, le premier principe s'écrit $\Delta U = Q + W$ ($W$ reçu) ou $\Delta U = Q - W$ ($W$ fourni). Fixer sa convention au début et s'y tenir. Voir [[Thermodynamique]].

> [!warning] Confondre chaleur et température
> La **température** mesure l'agitation thermique ; la **chaleur** est un transfert d'énergie. Deux corps de températures égales n'échangent pas de chaleur, quelle que soit leur taille.

> [!warning] Travailler en Celsius dans une formule de gaz parfait
> $PV = nRT$ exige $T$ en **kelvins**. Utiliser des °C donne des résultats absurdes (voire des températures négatives interdites).

## 4. Électricité

> [!warning] Sens conventionnel du courant
> Le courant conventionnel circule du $+$ vers le $-$ à l'extérieur du générateur, **à l'opposé** du déplacement réel des électrons. Source d'erreurs de signe en magnétisme et en induction.

> [!warning] Loi des mailles et orientation
> Avant d'écrire $\sum u = 0$, fixer un sens de parcours et l'orientation de chaque tension. Une flèche oubliée ou inversée change le signe du résultat.

> [!warning] Diviseur de tension sur charge
> La formule du pont diviseur de tension n'est valable que si **aucun courant** n'est tiré sur le point milieu. Brancher une charge en parallèle invalide la formule simple.

## 5. Ondes et optique

> [!warning] Confondre vitesse de l'onde et vitesse des particules
> Dans une onde mécanique, le **milieu oscille sur place** ; seule la perturbation se propage. La vitesse de propagation $v = \lambda f$ n'est pas la vitesse de vibration des particules.

> [!warning] Distances algébriques en optique
> Les relations de conjugaison utilisent des **distances algébriques** ($\overline{OA}$, $\overline{OA'}$, comptées avec un signe selon le sens de la lumière). Travailler en valeurs absolues mène à des erreurs de position et de nature d'image.

## 6. Relativité et quantique

> [!warning] Appliquer la mécanique classique à grande vitesse
> Pour $v$ comparable à $c$, additionner naïvement les vitesses est faux. Il faut la composition relativiste. À l'inverse, sortir le facteur $\gamma$ pour $v \ll c$ est inutile ($\gamma \approx 1$).

> [!warning] Le photon n'a pas de masse mais a une quantité de mouvement
> $p = \dfrac{h}{\lambda}$ pour un photon, bien que $m = 0$. La relation classique $p = mv$ ne s'applique pas aux particules sans masse.

## 7. Méthode générale

> [!warning] Le piège du calcul sans contrôle
> L'erreur la plus coûteuse est de foncer dans les calculs sans vérifier l'homogénéité, l'ordre de grandeur ni le signe du résultat. Voir [[Méthodes de Résolution]].

## 8. À retenir

> [!tip] À retenir
> - Une force modifie le mouvement, elle ne le maintient pas (inertie).
> - Masse $\neq$ poids ; température $\neq$ chaleur ; vitesse d'onde $\neq$ vitesse des particules.
> - En thermo, fixer sa convention de signe et travailler en kelvins.
> - En électricité et optique, soigner les **signes** et les **orientations**.
> - À grande vitesse : relativité. À l'échelle atomique : quantique.

*Voir aussi* : [[Méthodes de Résolution]] | [[Constantes et Unités]] | [[Index]]
