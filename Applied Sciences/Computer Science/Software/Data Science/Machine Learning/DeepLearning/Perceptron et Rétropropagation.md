---
title: "Perceptron et Rétropropagation"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > DeepLearning"
tags: [perceptron, mlp, rétropropagation, backpropagation, réseaux-de-neurones, deep-learning]
date: "2026-08-24"
prerequis: ["[[Apprentissage Supervisé]]", "[[Fonctions de pertes]]"]
---

# Perceptron et Rétropropagation

Avant le [[CNN]], le [[Transformers|Transformer]] ou le [[GAN]], il y a l'unité de base commune à tous les réseaux de neurones : le **neurone artificiel**, et l'algorithme qui permet de l'entraîner : la **rétropropagation** (backpropagation). Cette note pose les fondations sur lesquelles reposent toutes les architectures du dossier DeepLearning.

## Le neurone artificiel (Perceptron)

Un neurone reçoit plusieurs entrées, les combine linéairement avec des **poids**, ajoute un **biais**, puis applique une **fonction d'activation** non linéaire.

$$z = \sum_{i=1}^{n} w_i x_i + b, \qquad a = f(z)$$

```mermaid
flowchart LR
    X1["x₁"] -->|"w₁"| SUM["Σ + b"]
    X2["x₂"] -->|"w₂"| SUM
    X3["x₃"] -->|"w₃"| SUM
    SUM --> ACT["Fonction d'activation\nf(z)"]
    ACT --> OUT["Sortie a"]

    style SUM fill:#2196F3,color:#fff
    style ACT fill:#FF9800,color:#fff
    style OUT fill:#4CAF50,color:#fff
```

- $x_i$ : entrées (features ou sorties de la couche précédente)
- $w_i$ : poids — l'importance apprise de chaque entrée
- $b$ : biais — décale le seuil d'activation
- $f$ : fonction d'activation — introduit la **non-linéarité**, sans laquelle empiler des couches reviendrait à une simple combinaison linéaire, quel que soit le nombre de couches

### Apprendre une frontière

Rosenblatt entraîne le perceptron sans aucune dérivée : un point est classé selon le signe de $w_1 x_1 + w_2 x_2 + b$, et chaque fois que le perceptron se trompe sur un point, il **ajoute ce point à ses poids** (ou le retranche, selon sa classe). La droite pivote vers le point mal classé, et on recommence. Si une droite peut séparer les deux classes, cette règle finit toujours par en trouver une (théorème de convergence du perceptron).

> [!predict] Quatre groupes de points : en bas à gauche et en haut à droite la classe A, en haut à gauche et en bas à droite la classe B (c'est le XOR). Un perceptron seul peut-il apprendre à les séparer ?
> - [ ] Oui, s'il s'entraîne assez longtemps
>   Le temps n'y change rien : aucune droite ne laisse les deux groupes A d'un côté et les deux groupes B de l'autre.
> - [x] Non, aucune droite ne sépare ces points
>   Le perceptron corrige sans fin, sans jamais converger. C'est la limite pointée par Minsky et Papert en 1969.
> - [ ] Oui, avec un meilleur taux d'apprentissage
>   Pour le perceptron, le taux ne fait que changer l'échelle des poids, pas la droite qu'il peut tracer.

```widget:frontiere
modele: perceptron
jeu: separables
objectif: Entraînez le perceptron jusqu'à ce qu'il converge sur les points séparables.
cible: modele=perceptron, jeu=separables, converge=1
erreur: modele=logistique → Repassez sur le perceptron. ;; converge=0 → Pas encore : lancez l'entraînement jusqu'au bout.
bravo: Chaque correction a fait pivoter la droite vers le point cerclé, jusqu'à ce qu'aucun point ne reste du mauvais côté.
objectif-2: Chargez le XOR et lancez le perceptron. Attendez qu'il abandonne.
cible-2: modele=perceptron, jeu=xor, produit=0, abandon=1
erreur-2: produit=1 → Décochez la variable x₁·x₂ pour cet objectif. ;; jeu!=xor → Choisissez les points XOR. ;; abandon=0 → Laissez-le tourner : il corrige sans fin.
bravo-2: Quatre cents corrections, et toujours des points du mauvais côté : aucune droite ne sépare le XOR.
objectif-3: Ajoutez la variable x₁·x₂ et faites converger le perceptron sur le XOR.
cible-3: modele=perceptron, jeu=xor, produit=1, converge=1
indice-3: Cochez « Ajouter la variable x₁·x₂ », puis entraînez.
bravo-3: Avec une variable de plus, la frontière se courbe et le XOR devient séparable. Une couche cachée fait la même chose, mais apprend elle-même les variables utiles.
```

## Repères historiques

- **1958 — Perceptron (Rosenblatt)** : un seul neurone, capable d'apprendre des frontières linéaires
- **1969 — Limite du XOR (Minsky & Papert)** : un perceptron unique ne peut pas résoudre un problème non linéairement séparable comme le XOR — coup d'arrêt temporaire à la recherche sur les réseaux de neurones
- **1986 — Rétropropagation (Rumelhart, Hinton, Williams)** : algorithme permettant d'entraîner efficacement des réseaux **multicouches**, résolvant XOR et ouvrant la voie aux réseaux profonds

## Fonctions d'activation

| Fonction | Formule | Sortie | Problème |
|---|---|---|---|
| **Sigmoïde** | $\sigma(z) = \frac{1}{1+e^{-z}}$ | (0, 1) | Gradient proche de 0 aux extrêmes → vanishing gradient |
| **Tanh** | $\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}}$ | (-1, 1) | Centrée sur 0 (mieux que sigmoïde), mais même problème aux extrêmes |
| **ReLU** | $\max(0, z)$ | [0, +∞) | Simple, rapide, mais neurones "morts" si $z < 0$ en permanence |
| **Leaky ReLU** | $\max(0.01z, z)$ | (-∞, +∞) | Corrige les neurones morts |
| **GELU** | $z \cdot \Phi(z)$ (approximation lisse de ReLU) | ≈ [-0.17, +∞) | Utilisée dans les Transformers modernes |

**Pourquoi ReLU a supplanté sigmoïde/tanh dans les couches cachées** : son gradient vaut exactement 1 pour $z > 0$ (pas de saturation), ce qui limite le vanishing gradient et accélère considérablement l'entraînement des réseaux profonds. Sigmoïde reste utilisée en sortie pour une probabilité binaire (voir [[Apprentissage Supervisé]]), softmax pour une classification multi-classe.

## Le Perceptron Multicouche (MLP)

Un **MLP** (Multi-Layer Perceptron) empile plusieurs couches de neurones : une couche d'entrée, une ou plusieurs couches **cachées**, une couche de sortie.

```mermaid
flowchart LR
    subgraph "Couche d'entrée"
        I1((x₁))
        I2((x₂))
        I3((x₃))
    end
    subgraph "Couche cachée"
        H1((h₁))
        H2((h₂))
        H3((h₃))
        H4((h₄))
    end
    subgraph "Sortie"
        O1((ŷ))
    end
    I1 & I2 & I3 --> H1 & H2 & H3 & H4
    H1 & H2 & H3 & H4 --> O1
```

**Théorème d'approximation universelle** : un MLP avec une seule couche cachée suffisamment large peut approximer n'importe quelle fonction continue avec une précision arbitraire. En pratique, on préfère des réseaux **profonds** (plusieurs couches plus étroites) à un réseau **large** à une seule couche : ils apprennent des représentations hiérarchiques (les couches profondes combinent les motifs détectés par les couches précédentes) et généralisent souvent mieux pour un nombre de paramètres équivalent.

## La rétropropagation

**Le problème à résoudre** : après une prédiction, on connaît l'erreur en sortie (via la fonction de perte, voir [[Fonctions de pertes]]). Comment savoir de combien ajuster **chaque poids**, y compris ceux des couches profondes, loin de la sortie ?

**L'idée** : la règle de dérivation en chaîne (chain rule) permet de décomposer la dérivée de la perte par rapport à un poids profond en un produit de dérivées locales, couche par couche, en remontant de la sortie vers l'entrée.

$$\frac{\partial \mathcal{L}}{\partial w^{(l)}} = \frac{\partial \mathcal{L}}{\partial a^{(L)}} \cdot \frac{\partial a^{(L)}}{\partial a^{(L-1)}} \cdots \frac{\partial a^{(l+1)}}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial w^{(l)}}$$

Chaque terme est une dérivée simple, locale à une couche. Le produit de ces termes donne le gradient exact, sans jamais recalculer la fonction de perte entière pour chaque poids.

```mermaid
flowchart LR
    subgraph "Passe avant (forward)"
        direction LR
        X["Entrée x"] --> H1F["Couche 1"] --> H2F["Couche 2"] --> YF["Prédiction ŷ"]
        YF --> LOSS["Perte L(y, ŷ)"]
    end

    subgraph "Passe arrière (backward)"
        direction RL
        LOSS2["∂L/∂ŷ"] --> H2B["∂L/∂h₂\npuis ∂L/∂W₂"]
        H2B --> H1B["∂L/∂h₁\npuis ∂L/∂W₁"]
    end

    style LOSS fill:#FF5722,color:#fff
    style H2B fill:#FF9800,color:#fff
    style H1B fill:#FF9800,color:#fff
```

**Déroulement complet d'une itération d'entraînement :**

1. **Forward pass** : propager l'entrée à travers toutes les couches jusqu'à la prédiction
2. Calculer la **perte** entre prédiction et vérité terrain
3. **Backward pass** : appliquer la chain rule pour calculer le gradient de la perte par rapport à **chaque poids**, en remontant de la sortie vers l'entrée
4. **Mise à jour des poids** : utiliser ces gradients avec un optimiseur (descente de gradient, voir [[Apprentissage Supervisé]])

La rétropropagation ne fait que **calculer le gradient** efficacement — c'est ensuite la descente de gradient (batch, SGD, mini-batch, ou un optimiseur plus élaboré ci-dessous) qui l'utilise pour ajuster les poids.

## Optimiseurs

Au-delà de la descente de gradient simple, des optimiseurs plus élaborés accélèrent et stabilisent l'entraînement :

| Optimiseur | Idée clé | Quand l'utiliser |
|---|---|---|
| **SGD** | Descente de gradient stochastique de base | Baseline, souvent avec momentum |
| **Momentum** | Accumule une "vitesse" à partir des gradients passés — traverse les plateaux, amortit les oscillations | Accélère SGD dans les vallées étroites |
| **RMSprop** | Adapte le learning rate par paramètre selon la moyenne mobile des gradients au carré | Séries temporelles, RNN |
| **Adam** | Combine Momentum + RMSprop (moments d'ordre 1 et 2) | Choix par défaut dans la plupart des frameworks modernes |

```python
import torch.optim as optim

optimizer = optim.Adam(model.parameters(), lr=1e-3, betas=(0.9, 0.999))
```

## Initialisation des poids

> [!warning] Piège classique
> Initialiser tous les poids à **zéro** semble neutre mais casse l'entraînement : tous les neurones d'une couche calculeraient exactement la même chose et recevraient le même gradient, donc apprendraient de façon identique indéfiniment (symétrie jamais brisée). Une initialisation aléatoire est nécessaire, mais son échelle compte aussi — d'où Xavier et He ci-dessous.

| Méthode | Principe | Adaptée à |
|---|---|---|
| **Xavier / Glorot** | Variance des poids calibrée selon le nombre d'entrées et de sorties de la couche | Sigmoïde, tanh |
| **He** | Variante de Xavier adaptée à ReLU (facteur 2 supplémentaire) | ReLU et variantes |

## Problèmes courants

> [!warning] Pièges classiques
> - **Vanishing gradient** : dans un réseau profond avec sigmoïde/tanh, les gradients se multiplient à chaque couche en remontant — s'ils sont chacun < 1, le produit tend vers 0 et les premières couches n'apprennent presque plus. ReLU atténue ce problème ; les connexions résiduelles (voir [[CNN]] — ResNet) et la Batch Normalization le combattent aussi.
> - **Exploding gradient** : l'inverse — les gradients grandissent de façon incontrôlée. Solution courante : le **gradient clipping** (plafonner la norme du gradient).
> - **Neurones morts (dead ReLU)** : un neurone ReLU dont l'entrée reste négative ne produit plus jamais de gradient et cesse d'apprendre. Leaky ReLU ou GELU limitent ce risque.

## Régularisation spécifique au deep learning

Les techniques générales sont couvertes dans [[Biais-Variance et Régularisation]] ; deux méthodes sont spécifiques aux réseaux de neurones :

- **Dropout** : désactiver aléatoirement un pourcentage de neurones à chaque itération d'entraînement, forçant le réseau à ne pas dépendre excessivement d'un neurone particulier (voir [[CNN]])
- **Batch Normalization** : normalise les activations entre les couches, stabilise et accélère l'entraînement (détaillée dans [[CNN]])

## Exemple minimal

```python
import torch.nn as nn

mlp = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)

# Forward + backward + mise à jour, en une itération
pred = mlp(x)
loss = criterion(pred, y)
loss.backward()      # rétropropagation : calcule tous les gradients
optimizer.step()     # met à jour les poids avec les gradients calculés
optimizer.zero_grad()
```

## Questions

> [!quiz] Que fait le perceptron de Rosenblatt quand il classe mal un point ?
> Il ajoute ce point à ses poids s'il est de la classe positive, ou le retranche s'il est de la classe négative (et ajuste le biais de ±1). La frontière pivote vers le point mal classé.

> [!quiz] Pourquoi ne pas initialiser tous les poids d'un réseau à zéro ?
> - [ ] Parce que le réseau ne pourrait rien prédire du tout
>   Il prédit quelque chose, mais le problème est l'apprentissage, pas la première prédiction.
> - [x] Parce que tous les neurones d'une couche recevraient le même gradient et resteraient identiques
>   La symétrie n'est jamais brisée : une couche de cent neurones apprend comme un seul. D'où l'initialisation aléatoire (Xavier, He).
> - [ ] Parce que la rétropropagation divise par les poids
>   La rétropropagation multiplie des dérivées locales ; aucune division par les poids.

> [!quiz] Que calcule la rétropropagation, et que fait-elle de ce calcul ?
> Elle calcule le **gradient** de la perte par rapport à chaque poids, en appliquant la règle de dérivation en chaîne de la sortie vers l'entrée. Elle ne met pas à jour les poids : c'est l'optimiseur (descente de gradient, Adam…) qui s'en sert.

> [!quiz] Pourquoi ReLU a-t-elle remplacé la sigmoïde dans les couches cachées ?
> Son gradient vaut exactement 1 pour $z > 0$ : pas de saturation, donc le gradient ne s'éteint pas en remontant les couches (vanishing gradient), et l'entraînement des réseaux profonds est bien plus rapide.

## Liens

- [[Apprentissage Supervisé]] — descente de gradient, la mise à jour des poids qui utilise le gradient calculé par la rétropropagation
- [[Fonctions de pertes]] — les fonctions de perte dérivées lors du backward pass
- [[CNN]] — Batch Normalization, ReLU et connexions résiduelles en pratique
- [[Biais-Variance et Régularisation]] — dropout, early stopping et régularisation générale
- [[Transformers]] — GELU et architectures modernes construites sur ces fondations
