---
title: "Autoencoders"
domain: "Applied Sciences"
subdomain: "Computer Science > Data Science > Machine Learning > DeepLearning"
tags: [sciences-appliquées, informatique, data-science, machine-learning, deep-learning]
date: "2026-02-22"
---

# Autoencoders

Un **autoencoder** est un réseau de neurones entraîné à **reconstruire son entrée** en passant par une représentation compressée (le **code latent**). Il apprend à compresser les données de manière non-linéaire, puis à les reconstruire.

## Architecture de base

```mermaid
graph LR
    X["Entrée x<br/>(ex: image 784 px)"] --> ENC["Encodeur"]
    ENC --> Z["Code latent z<br/>(ex: 32 dimensions)"]
    Z --> DEC["Décodeur"]
    DEC --> XHAT["Reconstruction x̂<br/>(ex: image 784 px)"]

    X -.->|"Comparer : Loss = ||x - x̂||²"| XHAT

    style X fill:#2196F3,color:#fff
    style Z fill:#FF9800,color:#fff
    style XHAT fill:#4CAF50,color:#fff
```

| Composant | Rôle | Analogie |
|-----------|------|----------|
| **Encodeur** | Compresse l'entrée en un code latent de dimension réduite | Un résumé d'un livre |
| **Code latent (z)** | Représentation compressée — le "goulot d'étranglement" | Le résumé lui-même |
| **Décodeur** | Reconstruit l'entrée à partir du code latent | Réécrire le livre à partir du résumé |

**Fonction de perte :** erreur de reconstruction
$$\mathcal{L} = ||x - \hat{x}||^2 = \sum_i (x_i - \hat{x}_i)^2$$

Le réseau apprend les features les plus **importantes** pour pouvoir reconstruire — c'est une forme de **compression avec perte**.

## Types d'autoencoders

```mermaid
graph TB
    AE["Autoencoders"] --> UNDER["Undercomplete<br/>(compression)"]
    AE --> SPARSE["Sparse<br/>(contrainte de parcimonie)"]
    AE --> DENOISING["Denoising<br/>(résistance au bruit)"]
    AE --> VAE2["VAE<br/>(génératif)"]
    AE --> CONV["Convolutional<br/>(pour images)"]

    style AE fill:#673AB7,color:#fff
    style VAE2 fill:#4CAF50,color:#fff
    style DENOISING fill:#FF9800,color:#fff
```

### Undercomplete Autoencoder

Le type le plus simple : la dimension du code latent est **inférieure** à celle de l'entrée, forçant le réseau à apprendre une compression efficace.

- Si l'encodeur et le décodeur sont linéaires → équivalent à la **PCA**
- Avec des non-linéarités → capture des relations non-linéaires que PCA ne peut pas

### Sparse Autoencoder

Ajoute une **contrainte de parcimonie** : seuls quelques neurones du code latent doivent être activés simultanément.

$$\mathcal{L} = ||x - \hat{x}||^2 + \lambda \sum_j |z_j|$$

- Force le réseau à apprendre des features **distinctes** et **interprétables**
- Le code latent peut être de dimension supérieure à l'entrée (overcomplete)

### Denoising Autoencoder

L'entrée est **corrompue** (bruit ajouté), mais le réseau doit reconstruire l'entrée **originale** propre.

```mermaid
graph LR
    X["x (original)"] --> NOISE["+ Bruit"]
    NOISE --> XTILDE["x̃ (corrompu)"]
    XTILDE --> ENC2["Encodeur"]
    ENC2 --> Z2["z"]
    Z2 --> DEC2["Décodeur"]
    DEC2 --> XHAT2["x̂ ≈ x (propre)"]

    style NOISE fill:#F44336,color:#fff
    style XHAT2 fill:#4CAF50,color:#fff
```

- Apprend des représentations **robustes** au bruit
- Utilisé en **restauration d'images** et **débruitage**

### Convolutional Autoencoder

Utilise des couches de **convolution** (encodeur) et de **convolution transposée** (décodeur) au lieu de couches denses. Adapté aux **images**.

## Variational Autoencoder (VAE)

Le VAE est la variante la plus importante. Contrairement à un autoencoder classique, il apprend une **distribution** dans l'espace latent, ce qui en fait un **modèle génératif**.

### Différence fondamentale

| | Autoencoder classique | VAE |
|---|---|---|
| **Code latent** | Un point fixe $z$ | Une distribution $q(z \mid x) = \mathcal{N}(\mu, \sigma^2)$ |
| **Espace latent** | Désordonné, pas de structure | **Continu et structuré** |
| **Génération** | Difficile (pas de structure) | Échantillonner $z \sim \mathcal{N}(\mu, \sigma^2)$ et décoder |
| **Utilisation** | Compression, débruitage | Génération de nouvelles données |

### Architecture du VAE

```mermaid
graph LR
    X3["Entrée x"] --> ENC3["Encodeur"]
    ENC3 --> MU["μ (moyenne)"]
    ENC3 --> SIGMA["σ (écart-type)"]
    MU --> SAMPLE["Échantillonnage<br/>z = μ + σ × ε<br/>ε ~ N(0,1)"]
    SIGMA --> SAMPLE
    SAMPLE --> DEC3["Décodeur"]
    DEC3 --> XHAT3["Reconstruction x̂"]

    style X3 fill:#2196F3,color:#fff
    style SAMPLE fill:#FF9800,color:#fff
    style XHAT3 fill:#4CAF50,color:#fff
```

### Fonction de perte du VAE

La loss du VAE combine deux termes :

$$\mathcal{L} = \underbrace{||x - \hat{x}||^2}_{\text{Reconstruction}} + \underbrace{D_{KL}\big(q(z|x) \;\|\; p(z)\big)}_{\text{Régularisation}}$$

| Terme | Rôle |
|-------|------|
| **Reconstruction** | La sortie doit ressembler à l'entrée |
| **KL Divergence** | L'espace latent doit ressembler à une distribution normale $\mathcal{N}(0, 1)$ |

La **KL Divergence** est cruciale : elle force l'espace latent à être **régulier** et **continu**, ce qui permet de **générer** de nouvelles données en échantillonnant.

### Le reparameterization trick

Problème : l'échantillonnage $z \sim q(z|x)$ n'est **pas différentiable** — on ne peut pas rétro-propager.

Solution : réécrire l'échantillonnage comme :
$$z = \mu + \sigma \odot \varepsilon, \quad \varepsilon \sim \mathcal{N}(0, I)$$

Le caractère aléatoire est isolé dans $\varepsilon$ (qui ne dépend pas des paramètres), et $\mu$ et $\sigma$ restent différentiables.

## Applications

| Application | Type d'autoencoder | Description |
|-------------|-------------------|-------------|
| **Réduction de dimensionnalité** | Undercomplete | Alternative non-linéaire à PCA |
| **Détection d'anomalies** | Tous types | Erreur de reconstruction élevée = anomalie |
| **Débruitage d'images** | Denoising | Restaurer des images corrompues |
| **Génération de données** | VAE | Créer de nouveaux visages, molécules, musique |
| **Interpolation** | VAE | Transitions fluides entre deux images dans l'espace latent |
| **Compression** | Convolutional | Compresser des images avec moins de perte que JPEG |
| **Apprentissage de représentations** | Tous types | Pré-entraîner des features pour d'autres tâches |

## VAE vs GAN

| Critère | VAE | GAN |
|---------|-----|-----|
| **Entraînement** | Stable (une seule loss) | Instable (jeu à 2 joueurs) |
| **Qualité des images** | Floues (tendance à moyenner) | Nettes et réalistes |
| **Diversité** | Bonne (espace latent régulier) | Risque de mode collapse |
| **Espace latent** | Structuré, interprétable | Non structuré |
| **Évaluation** | ELBO (objectif clair) | Pas de métrique simple |

> Les VAE produisent des images plus **floues** mais offrent un espace latent **structuré**. Les GAN produisent des images plus **nettes** mais sont plus difficiles à entraîner.
